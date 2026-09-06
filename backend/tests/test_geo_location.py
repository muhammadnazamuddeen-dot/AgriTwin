"""Unit & Integration tests for Reverse Geocoding & Geographic Utilities."""

import pytest
from app.services.geo import compute_area_and_centroid, find_nearest_district, reverse_geocode


def test_find_nearest_district_centroids():
    """Test nearest district lookup for major Pakistani coordinates."""
    # Gujrat coordinates (32.5736, 74.0782)
    res_gujrat = find_nearest_district(32.57, 74.08)
    assert res_gujrat["district"] == "Gujrat"
    assert res_gujrat["province"] == "Punjab"

    # Multan coordinates (30.1575, 71.5249)
    res_multan = find_nearest_district(30.16, 71.52)
    assert res_multan["district"] == "Multan"
    assert res_multan["province"] == "Punjab"

    # Peshawar coordinates (34.0151, 71.5249)
    res_peshawar = find_nearest_district(34.01, 71.52)
    assert res_peshawar["district"] == "Peshawar"
    assert res_peshawar["province"] == "KPK"

    # Sukkur coordinates (27.7052, 68.8574)
    res_sukkur = find_nearest_district(27.70, 68.85)
    assert res_sukkur["district"] == "Sukkur"
    assert res_sukkur["province"] == "Sindh"


@pytest.mark.asyncio
async def test_reverse_geocode_fallback():
    """Test reverse_geocode always returns valid district/province for Pakistani coordinates."""
    # Test valid Pakistani coordinates (Gujrat)
    geo_res = await reverse_geocode(32.5736, 74.0782)
    assert geo_res["district"] != ""
    assert geo_res["province"] != ""


def test_reverse_geocode_endpoint(authenticated_client):
    """Test GET /api/v1/farms/reverse-geocode endpoint."""
    client = authenticated_client
    res = client.get("/api/v1/farms/reverse-geocode?lat=31.4187&lon=73.0791")
    assert res.status_code == 200
    data = res.json()
    assert "district" in data
    assert "province" in data
    assert data["district"] in ["Faisalabad", "Faisalabad District", "Punjab"] or data["province"] == "Punjab"


def test_farm_creation_auto_reverse_geocode(authenticated_client):
    """Test farm creation auto-enriches district and province from lat/lon even without polygon."""
    client = authenticated_client
    payload = {
        "name": "Auto Geo Test Farm",
        "latitude": 30.1575,
        "longitude": 71.5249,
        "area_acres": 10.0,
    }
    res = client.post("/api/v1/farms/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["district"] is not None
    assert "Multan" in data["district"]
    assert data["province"] == "Punjab"
