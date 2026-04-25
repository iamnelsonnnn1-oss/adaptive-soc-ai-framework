# Adaptive SOC AI Framework
**Version: 1.0**

A fully automated, Infrastructure-as-Code (IaC) driven Security Operations Center (SOC) framework with integrated SIEM, SOAR, and AI-driven anomaly detection.

This platform is designed to deliver adaptive threat detection and automated response using both supervised and unsupervised learning (**Isolation Forest**), built on a modular and scalable architecture.

---

## Project Architecture (Visual System Topology)

![System Topology](docs/diagrams/topology.png)

*The framework is organized into color-coordinated functional phases to ensure a systematic, scalable, and modular build-out.*

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