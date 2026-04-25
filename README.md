# Adaptive SOC AI Framework
**Version: 1.0**

A fully automated, Infrastructure-as-Code (IaC) driven Security Operations Center (SOC) framework with integrated SIEM, SOAR, and AI-driven anomaly detection.

This platform is designed to deliver adaptive threat detection and automated response using both supervised and unsupervised learning (**Isolation Forest**), built on a modular and scalable architecture.

---

## Project Structure (Full System Topology)

adaptive-soc-ai-framework/
├── README.md
├── LICENSE
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── core_framework/
│   ├── 1_Infrastructure_IaC/   # Terraform, Ansible, Docker, Kubernetes
│   ├── 2_Data_Sources/         # Telemetry and Log origin definitions
│   ├── 3_Log_Collection/       # Ingestion and pipeline logic
│   ├── 4_SIEM/                 # ELK Stack / Chronicle
│   ├── 5_AI_Detection/         # Isolation Forest & Supervised models
│   ├── 6_Alerts/               # Alert classification and logic
│   ├── 7_SOAR/                 # Tines automation workflows
│   └── 8_Response_Actions/     # LimaCharlie EDR mitigation
├── soc_variants/
│   ├── cloud_soc/              # CSPM and Cloud-native focus
│   ├── enterprise_soc/         # Multi-tenant/High-scale configuration
│   ├── zero_trust_soc/         # Identity-centric architecture
│   └── smb_soc/                # Lean, cost-effective framework
└── docs/
    ├── architecture.md
    ├── diagrams/
    └── playbooks/

---

## AI Capabilities

* **Supervised Learning:** Detects known threats and categorized attack patterns.
* **Unsupervised Learning:** Isolation Forest for behavior-based anomaly detection.
* **Behavioral Analysis:** Identifies zero-day threats by monitoring system baselines.

---

## Security Stack

* **SOAR:** Tines
* **EDR:** LimaCharlie
* **IDS/IPS:** Suricata
* **SIEM:** ELK Stack / Chronicle (optional)

---

## DevSecOps Integration

* **GitHub Actions:** Automated CI/CD pipelines.
* **Terraform:** Dynamic infrastructure validation.
* **Ansible:** Playbook testing and configuration management.
* **Docker:** Container security and validation.
* **Playwright:** Optional end-to-end testing for SOC dashboards.

---

## Core Principles

* **Adaptive:** Learns and evolves with threats.
* **Modular:** Easily customizable per client or environment.
* **Scalable:** Cloud-ready architecture utilizing European zones.
* **Automated:** End-to-end detection to response pipeline.
* **Git-First:** Everything is version-controlled and documented.

---

## Author

**Nelson Ortiz**
GitHub: [iamnelsonnnn1-oss](https://github.com/iamnelsonnnn1-oss)