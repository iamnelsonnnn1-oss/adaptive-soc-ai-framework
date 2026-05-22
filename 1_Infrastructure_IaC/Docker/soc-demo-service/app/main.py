from datetime import datetime, timezone

from fastapi import FastAPI


app = FastAPI(
    title="Adaptive SOC Demo Service",
    version="1.0.0",
    description="Demo-ready API for validating the SOC framework Docker layer.",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "soc-demo-service",
        "timestamp": utc_now(),
    }


@app.get("/framework")
def framework() -> dict:
    return {
        "name": "adaptive-soc-ai-framework",
        "region": "eu-central-1",
        "layers": [
            "terraform",
            "ansible",
            "docker",
        ],
        "handoff": {
            "terraform": "provisions the AWS foundation and governance tags",
            "ansible": "consumes the infrastructure contract and prepares hosts",
            "docker": "packages and runs demo workloads consistently",
        },
        "timestamp": utc_now(),
    }


@app.get("/telemetry")
def telemetry() -> dict:
    alerts = [
        {
            "id": "evt-1001",
            "severity": "medium",
            "source": "suricata",
            "category": "network-anomaly",
            "status": "triaged",
        },
        {
            "id": "evt-1002",
            "severity": "high",
            "source": "darktrace",
            "category": "behavioral-anomaly",
            "status": "investigating",
        },
        {
            "id": "evt-1003",
            "severity": "low",
            "source": "limacharlie",
            "category": "endpoint-observation",
            "status": "open",
        },
    ]

    return {
        "service": "soc-demo-service",
        "summary": {
            "total_alerts": len(alerts),
            "open_alerts": len([alert for alert in alerts if alert["status"] != "triaged"]),
        },
        "alerts": alerts,
        "timestamp": utc_now(),
    }
