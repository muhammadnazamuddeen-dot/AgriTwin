"""Geographic utilities — area, centroid, and reverse geocoding.

Uses:
  - shapely for GeoJSON parsing and centroid computation
  - Geodesic area via the spherical excess formula (no extra deps)
  - Nominatim (OpenStreetMap) for reverse geocoding district / province
"""

import json
import logging
import math

import httpx
from shapely.geometry import shape

logger = logging.getLogger(__name__)

# WGS-84 mean Earth radius in metres
_EARTH_RADIUS_M = 6_371_008.8


# ── Geodesic polygon area (spherical) ───────────────────────────────────────
def _geodesic_area_sqm(coords: list[tuple[float, float]]) -> float:
    """Compute the geodesic area in square metres for a polygon ring.

    Uses the spherical excess formula on WGS-84 mean radius.
    *coords* is a list of (lon, lat) pairs — GeoJSON order.
    """
    n = len(coords)
    if n < 3:
        return 0.0

    total = 0.0
    for i in range(n):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[(i + 1) % n]
        lon3, lat3 = coords[(i + 2) % n]
        total += (math.radians(lon3) - math.radians(lon1)) * math.sin(
            math.radians(lat2)
        )
    area = abs(total * _EARTH_RADIUS_M**2 / 2)
    return area


# ── Public API ───────────────────────────────────────────────────────────────
def compute_area_and_centroid(geojson_str: str) -> dict:
    """Return area_acres, latitude, longitude from a GeoJSON polygon string.

    Accepts any GeoJSON geometry (Polygon, MultiPolygon).  Returns::

        {"area_acres": float, "latitude": float, "longitude": float}
    """
    geom = shape(json.loads(geojson_str))
    centroid = geom.centroid

    # Collect exterior ring(s) for area calculation
    if geom.geom_type == "Polygon":
        rings = [list(geom.exterior.coords)]
    elif geom.geom_type == "MultiPolygon":
        rings = [list(p.exterior.coords) for p in geom.geoms]
    else:
        rings = []

    total_sqm = sum(_geodesic_area_sqm(r) for r in rings)
    area_acres = round(total_sqm / 4046.8564224, 2)

    return {
        "area_acres": area_acres,
        "latitude": round(centroid.y, 6),
        "longitude": round(centroid.x, 6),
    }


# ── Pakistan District Centroid Fallback Database ─────────────────────────────
PAKISTAN_DISTRICT_CENTROIDS = [
    # Punjab
    {"district": "Gujrat", "province": "Punjab", "lat": 32.5736, "lon": 74.0782},
    {"district": "Gujranwala", "province": "Punjab", "lat": 32.1617, "lon": 74.1883},
    {"district": "Sialkot", "province": "Punjab", "lat": 32.4945, "lon": 74.5229},
    {"district": "Faisalabad", "province": "Punjab", "lat": 31.4187, "lon": 73.0791},
    {"district": "Lahore", "province": "Punjab", "lat": 31.5204, "lon": 74.3587},
    {"district": "Sheikhupura", "province": "Punjab", "lat": 31.7167, "lon": 73.9850},
    {"district": "Kasur", "province": "Punjab", "lat": 31.1167, "lon": 74.4500},
    {"district": "Multan", "province": "Punjab", "lat": 30.1575, "lon": 71.5249},
    {"district": "Khanewal", "province": "Punjab", "lat": 30.3017, "lon": 71.9321},
    {"district": "Sahiwal", "province": "Punjab", "lat": 30.6682, "lon": 73.1114},
    {"district": "Okara", "province": "Punjab", "lat": 30.8081, "lon": 73.4458},
    {"district": "Vehari", "province": "Punjab", "lat": 30.0419, "lon": 72.3528},
    {"district": "Bahawalpur", "province": "Punjab", "lat": 29.3956, "lon": 71.6836},
    {"district": "Rahim Yar Khan", "province": "Punjab", "lat": 28.4212, "lon": 70.2989},
    {"district": "Sargodha", "province": "Punjab", "lat": 32.0836, "lon": 72.6711},
    {"district": "Jhang", "province": "Punjab", "lat": 31.2681, "lon": 72.3181},
    {"district": "Toba Tek Singh", "province": "Punjab", "lat": 30.9748, "lon": 72.4826},
    {"district": "Mianwali", "province": "Punjab", "lat": 32.5853, "lon": 71.5436},
    {"district": "Bhakkar", "province": "Punjab", "lat": 31.6253, "lon": 71.0653},
    {"district": "Layyah", "province": "Punjab", "lat": 30.9613, "lon": 70.9390},
    {"district": "Muzaffargarh", "province": "Punjab", "lat": 30.0754, "lon": 71.1921},
    {"district": "Dera Ghazi Khan", "province": "Punjab", "lat": 30.0561, "lon": 70.6340},
    {"district": "Bahawalnagar", "province": "Punjab", "lat": 29.9987, "lon": 73.2536},
    {"district": "Chakwal", "province": "Punjab", "lat": 32.9328, "lon": 72.8530},
    {"district": "Jhelum", "province": "Punjab", "lat": 32.9405, "lon": 73.7276},
    {"district": "Rawalpindi", "province": "Punjab", "lat": 33.5651, "lon": 73.0169},
    {"district": "Attock", "province": "Punjab", "lat": 33.7667, "lon": 72.3592},
    {"district": "Mandi Bahauddin", "province": "Punjab", "lat": 32.5861, "lon": 73.4917},
    {"district": "Nankana Sahib", "province": "Punjab", "lat": 31.4492, "lon": 73.7124},
    {"district": "Hafizabad", "province": "Punjab", "lat": 32.0709, "lon": 73.6880},
    {"district": "Narowal", "province": "Punjab", "lat": 32.1020, "lon": 74.8730},
    {"district": "Chiniot", "province": "Punjab", "lat": 31.7200, "lon": 72.9780},
    {"district": "Khushab", "province": "Punjab", "lat": 32.2952, "lon": 72.3502},
    {"district": "Lodhran", "province": "Punjab", "lat": 29.5339, "lon": 71.6324},
    {"district": "Rajanpur", "province": "Punjab", "lat": 29.1044, "lon": 70.3301},

    # Sindh
    {"district": "Hyderabad", "province": "Sindh", "lat": 25.3960, "lon": 68.3578},
    {"district": "Sukkur", "province": "Sindh", "lat": 27.7052, "lon": 68.8574},
    {"district": "Larkana", "province": "Sindh", "lat": 27.5589, "lon": 68.2120},
    {"district": "Shaheed Benazirabad", "province": "Sindh", "lat": 26.2483, "lon": 68.4096},
    {"district": "Mirpur Khas", "province": "Sindh", "lat": 25.5269, "lon": 69.0159},
    {"district": "Karachi", "province": "Sindh", "lat": 24.8607, "lon": 67.0011},

    # KPK
    {"district": "Peshawar", "province": "KPK", "lat": 34.0151, "lon": 71.5249},
    {"district": "Mardan", "province": "KPK", "lat": 34.1989, "lon": 72.0404},
    {"district": "Swabi", "province": "KPK", "lat": 34.1202, "lon": 72.4698},
    {"district": "Dera Ismail Khan", "province": "KPK", "lat": 31.8314, "lon": 70.9019},

    # Balochistan
    {"district": "Quetta", "province": "Balochistan", "lat": 30.1798, "lon": 66.9750},
    {"district": "Jaffarabad", "province": "Balochistan", "lat": 28.4310, "lon": 68.0123},
]


def find_nearest_district(lat: float, lon: float) -> dict:
    """Find the nearest Pakistani district and province for given lat/lon."""
    best_item = PAKISTAN_DISTRICT_CENTROIDS[0]
    min_dist_sq = float("inf")
    for item in PAKISTAN_DISTRICT_CENTROIDS:
        dist_sq = (lat - item["lat"]) ** 2 + (lon - item["lon"]) ** 2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_item = item
    return {"district": best_item["district"], "province": best_item["province"]}


def _clean_district_name(raw_district: str) -> str:
    """Clean district name returned by Nominatim."""
    if not raw_district:
        return ""
    clean = raw_district
    for suffix in [" District", " Tehsil", " Division", " City", " Zilla"]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)]
    return clean.strip()


async def reverse_geocode(lat: float, lon: float) -> dict:
    """Resolve *lat*/*lon* to district and province via Nominatim with nearest-centroid fallback.

    Returns ``{"district": str, "province": str}``.
    """
    is_pk = (23.0 <= lat <= 37.5) and (60.0 <= lon <= 78.0)
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10, "accept-language": "en"}
    headers = {"User-Agent": "AgriTwin-AI/0.1"}

    district = ""
    province = ""

    try:
        async with httpx.AsyncClient(timeout=4) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        address = data.get("address", {})
        raw_district = (
            address.get("county")
            or address.get("district")
            or address.get("city")
            or address.get("town")
            or ""
        )
        district = _clean_district_name(raw_district)
        province = address.get("state", "")
    except Exception as exc:
        logger.warning("Reverse geocoding OSM request failed for (%s, %s): %s", lat, lon, exc)

    # If Nominatim returned empty district or failed, and coordinates are in Pakistan, use centroid fallback!
    if (not district or not province) and is_pk:
        fallback = find_nearest_district(lat, lon)
        if not district:
            district = fallback["district"]
        if not province:
            province = fallback["province"]

    return {"district": district or ("Gujrat" if is_pk else ""), "province": province or ("Punjab" if is_pk else "")}


async def get_ip_location() -> dict:
    """Resolve location estimate from client IP with fallback to Pakistani centroid."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get("https://ipapi.co/json/")
            if resp.status_code == 200:
                data = resp.json()
                lat = data.get("latitude")
                lon = data.get("longitude")
                if lat is not None and lon is not None:
                    geo = find_nearest_district(float(lat), float(lon))
                    return {
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "district": geo["district"],
                        "province": geo["province"],
                        "source": "ip_geolocation",
                    }
    except Exception as exc:
        logger.warning("IP geolocation request failed: %s", exc)

    return {
        "latitude": 32.5736,
        "longitude": 74.0782,
        "district": "Gujrat",
        "province": "Punjab",
        "source": "default_pakistan",
    }


