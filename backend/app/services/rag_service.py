"""
AgriTwin AI — RAG Layer & Agricultural Knowledge Retrieval Service (Phase 12).
Retrieves official Punjab Agriculture Department advisories, pest bulletins, and crop calendar facts.
"""

from app.core.engine.crop_knowledge import CROP_KNOWLEDGE_BASE, get_crop_info
from app.services.seasonal_advisory_service import seasonal_advisory_engine

class RAGKnowledgeService:
    def retrieve_advisory(self, crop_name: str | None, district: str | None = None, telemetry: dict | None = None, language: str = "en") -> str:
        if not crop_name:
            return "Ensure regular crop monitoring, soil testing, and balanced fertilizer application."

        info = get_crop_info(crop_name)
        advisory_parts = []

        # Real-Time Seasonal & Monthly Advisory
        seasonal_res = seasonal_advisory_engine.get_seasonal_recommendation(crop_name, district, telemetry)
        if language == "pa":
            advisory_parts.append(seasonal_res["advisory_pa"])
        else:
            advisory_parts.append(seasonal_res["advisory_en"])

        if info:
            if "advisory_2026" in info:
                advisory_parts.append(info["advisory_2026"])
            if "common_pests" in info:
                advisory_parts.append(f"Monitor for major pests: {', '.join(info['common_pests'])}.")
            if "sowing_window" in info:
                advisory_parts.append(f"Optimal Sowing Window: {info['sowing_window']}.")

        return " ".join(advisory_parts)

rag_service = RAGKnowledgeService()
