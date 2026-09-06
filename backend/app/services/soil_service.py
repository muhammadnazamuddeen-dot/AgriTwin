"""Soil data service — integrates SoilGrids REST API for static soil properties."""

import httpx


class SoilService:
    """Fetch static soil properties from ISRIC SoilGrids (free, no API key)."""

    SOILGRIDS_URL = "https://rest.isric.org/soil-properties/query"

    # SoilGrids property codes → friendly names
    _PROPERTIES = ["phh2o", "soc", "clay", "sand", "silt", "bdod"]
    # Depth layers to query (average across 0-30 cm topsoil)
    _DEPTHS = ["0-5cm", "5-15cm", "15-30cm"]

    async def get_soil_profile(self, lat: float, lon: float) -> dict | None:
        """Fetch static soil properties from SoilGrids REST API.

        Returns a dict with averaged topsoil (0-30 cm) properties, or None on failure.
        """
        params = {
            "lon": lon,
            "lat": lat,
            "property": self._PROPERTIES,
            "depth": self._DEPTHS,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(self.SOILGRIDS_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception:
            return None

        # SoilGrids returns: { "properties": { "phh2o": { "0-5cm": {"value": ..., "uncertainty": ...}, ... }, ... } }
        props = data.get("properties", {})
        if not props:
            return None

        def _avg_depth(prop_code: str) -> float | None:
            """Average the mean values across queried depth layers."""
            prop_data = props.get(prop_code, {})
            if not isinstance(prop_data, dict):
                return None
            values = []
            for depth in self._DEPTHS:
                layer = prop_data.get(depth, {})
                if isinstance(layer, dict):
                    v = layer.get("value")
                    if v is not None and v != -9999:
                        values.append(float(v))
            if not values:
                return None
            return round(sum(values) / len(values), 2)

        # SoilGrids unit conversions:
        #   phh2o: pH * 10 (integer) → divide by 10
        #   soc: g/kg * 10 → divide by 10
        #   clay/sand/silt: g/kg * 10 → divide by 10 to get %
        #   bdod: kg/dm3 * 100 → divide by 100
        ph_raw = _avg_depth("phh2o")
        soc_raw = _avg_depth("soc")
        clay_raw = _avg_depth("clay")
        sand_raw = _avg_depth("sand")
        silt_raw = _avg_depth("silt")
        bd_raw = _avg_depth("bdod")

        return {
            "ph_topsoil": round(ph_raw / 10, 1) if ph_raw is not None else None,
            "organic_carbon_g_per_kg": round(soc_raw / 10, 1) if soc_raw is not None else None,
            "clay_pct": round(clay_raw / 10, 1) if clay_raw is not None else None,
            "sand_pct": round(sand_raw / 10, 1) if sand_raw is not None else None,
            "silt_pct": round(silt_raw / 10, 1) if silt_raw is not None else None,
            "bulk_density_kg_dm3": round(bd_raw / 100, 2) if bd_raw is not None else None,
            "source": "soilgrids",
        }


soil_service = SoilService()
