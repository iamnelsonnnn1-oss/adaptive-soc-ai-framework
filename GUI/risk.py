import streamlit as st

class RiskPostureService:
    def calculate_score(self, threats: list) -> dict:
        """Splunk ES style security posture calculation."""
        if not threats:
            return {"score": 100, "rating": "GOLD", "label": "SECURE"}
        
        critical_count = len([t for t in threats if t.get('Severity') == 'Critical'])
        high_count = len([t for t in threats if t.get('Severity') == 'High'])
        
        # Posture degrades based on urgency hierarchy
        penalty = (critical_count * 25) + (high_count * 10)
        score = max(0, 100 - penalty)
        
        rating = "GOLD" if score > 90 else "SILVER" if score > 70 else "BRONZE"
        label = "MASTER CAUTION" if critical_count > 0 else "DEGRADED" if high_count > 0 else "STABLE"
        
        return {"score": score, "rating": rating, "label": label}

@st.cache_resource
def get_risk_service():
    return RiskPostureService()