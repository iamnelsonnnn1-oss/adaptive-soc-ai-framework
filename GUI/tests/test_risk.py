import risk


def make_service():
    return risk.RiskPostureService()


def test_empty_threats_returns_secure_gold():
    result = make_service().calculate_score([])
    assert result == {"score": 100, "rating": "GOLD", "label": "SECURE"}


def test_single_high_threat_degrades_score():
    threats = [{"Severity": "High"}]
    result = make_service().calculate_score(threats)
    assert result["score"] == 90
    # 90 is not > 90, so rating drops out of GOLD
    assert result["rating"] == "SILVER"
    assert result["label"] == "DEGRADED"


def test_single_critical_threat_triggers_master_caution():
    threats = [{"Severity": "Critical"}]
    result = make_service().calculate_score(threats)
    assert result["score"] == 75
    assert result["rating"] == "SILVER"
    assert result["label"] == "MASTER CAUTION"


def test_score_never_goes_below_zero():
    threats = [{"Severity": "Critical"}] * 10
    result = make_service().calculate_score(threats)
    assert result["score"] == 0
    assert result["rating"] == "BRONZE"
    assert result["label"] == "MASTER CAUTION"


def test_mixed_severities_penalty_math():
    threats = [
        {"Severity": "Critical"},
        {"Severity": "High"},
        {"Severity": "High"},
        {"Severity": "Low"},
        {"Severity": "Medium"},
    ]
    # penalty = 1*25 + 2*10 = 45 -> score 55
    result = make_service().calculate_score(threats)
    assert result["score"] == 55
    assert result["rating"] == "BRONZE"
    assert result["label"] == "MASTER CAUTION"


def test_high_only_label_is_degraded_not_master():
    threats = [{"Severity": "High"}, {"Severity": "High"}]
    # penalty = 20 -> score 80
    result = make_service().calculate_score(threats)
    assert result["score"] == 80
    assert result["rating"] == "SILVER"
    assert result["label"] == "DEGRADED"


def test_only_non_critical_high_threats_are_stable():
    threats = [{"Severity": "Low"}, {"Severity": "Medium"}]
    # no critical/high penalty -> score stays 100
    result = make_service().calculate_score(threats)
    assert result["score"] == 100
    assert result["rating"] == "GOLD"
    assert result["label"] == "STABLE"


def test_threats_without_severity_key_are_ignored():
    threats = [{"foo": "bar"}, {}]
    result = make_service().calculate_score(threats)
    assert result["score"] == 100
    assert result["label"] == "STABLE"


def test_get_risk_service_returns_service_instance():
    # The cache_resource decorator wraps the factory; calling it should still
    # yield a working RiskPostureService.
    service = risk.get_risk_service()
    assert isinstance(service, risk.RiskPostureService)
