# NetDevOps Closed-Loop Active Self-Healing Platform

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/n8n-Orchestrator-EA4B71?logo=n8n&logoColor=white" alt="n8n" />
  <img src="https://img.shields.io/badge/NetBox-SSoT-004D40?logo=netbox&logoColor=white" alt="NetBox" />
  <img src="https://img.shields.io/badge/Fortinet-FortiOS_REST_API-EE3124?logo=fortinet&logoColor=white" alt="Fortinet" />
  <img src="https://img.shields.io/badge/Netmiko-PEP_668-blue" alt="Netmiko" />
  <img src="https://img.shields.io/badge/PRTG-Webhooks-green" alt="PRTG" />
  <img src="https://img.shields.io/badge/MongoDB-Audit_Trail-47A248?logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Metabase-BI_Analytics-509EE3?logo=metabase&logoColor=white" alt="Metabase" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
</p>

> **Enterprise Hybrid Network Auto-Remediation (In collaboration with ARTE, I.P.)**  
> Active self-healing orchestration for hybrid corporate networks (Underlay MPLS + Overlay IPsec FortiGate VPN), reducing incident response and recovery times from **15–30 minutes to deterministic 40–70 seconds**.

---

## 🛠️ Tech Stack

* **Orchestration & Workflow Engine:** `n8n` (State Machine with event-driven execution)
* **Single Source of Truth (SSoT):** `NetBox` (IPAM / DCIM canonical state reconciliation)
* **Target Network Hardware & API:** `Fortinet FortiGate (FortiOS 7.x REST API CMDB)`
* **Contingency Execution:** `Python 3.11` + `Netmiko` (Out-of-band SSH engine under PEP 668 compliance)
* **Monitoring & Triggers:** `PRTG Network Monitor` (Automated webhook payloads)
* **Data Persistence & Audit:** `MongoDB` (Immutable event ledger & timing metrics)
* **Analytics & Telemetry:** `Metabase` (Real-time MTTR visualization & SLA reporting)
* **Infrastructure Packaging:** `Docker` & `Docker Compose`

---

## 🔥 Key Highlights & What Was Built

* 🔄 **Event-Driven Closed-Loop Orchestration:** Autonomous detection via PRTG webhooks triggering deterministic state machines in n8n.
* 📖 **Single Source of Truth (SSoT):** Runtime network state validation and configuration drift prevention against NetBox IPAM/DCIM.
* ⚡ **Synchronous Remediation:** Direct CMDB patch operations via FortiOS REST API secured with token-based authentication and trusted host restrictions.
* 🛡️ **Out-of-Band Fallback Engine:** Resilient CLI contingency engine written in Python (Netmiko) running in isolated virtual environments under PEP 668 to bypass API write-license constraints.
* 🧪 **Chaos Engineering Audits:** 24 fault-injection scenarios systematically tested (link drops, BGP flaps, API timeouts), achieving 100% automated recovery.
* 📊 **Telemetry & Audit Trail:** Real-time MTTR calculations in Metabase with immutable incident logs stored in MongoDB.

---

## 🏛️ Lab Network Topology & Segmentation

The virtual environment was deployed on **VMware Workstation Pro** with strict **Out-of-Band (OOB) management segregation** to guarantee automation control plane availability:

<p align="center">
  <img src="docs/topology.png" width="90%" alt="Lab Topology & VMware Segmentation" style="border-radius: 8px;" />
</p>

### 🔌 Physical & Virtual Interface Mapping

* **🛡️ Management Network (OOB):** Dedicated segment hosting PRTG and the n8n automation stack (`10.0.0.0/24` — Port2 on FortiGate HUB).
* **🌐 Underlay MPLS Transport:** Point-to-point simulated leased line between HUB and SPOKE (`172.16.0.0/30` — Port3 on HUB `172.16.0.1` ↔ Port2 on SPOKE `172.16.0.2`).
* **🔒 Overlay IPsec VPN:** Encrypted point-to-point tunnel (`10.10.10.0/30` — Port1 on HUB `10.10.10.1` ↔ Port3 on SPOKE `10.10.10.2`).
* **🏬 SPOKE LAN:** Emulated branch office local network (`192.168.10.0/24` — Port1 on FortiGate SPOKE `192.168.10.1`).

---

## 🔄 Autonomous Decision Logic & Closed-Loop Flow

The orchestration engine implements a deterministic decision tree to isolate root causes and execute surgical remediations across 4 distinct failure domains:

<p align="center">
  <img src="docs/closed_loop_flowchart.png" width="80%" alt="Closed Loop Decision Flow" style="border-radius: 8px;" />
</p>

### 🧠 Root-Cause Isolation & Remediation Stages

1. **Pre-Check Phase:** Validates the physical Underlay circuit (MPLS) to prevent false-positive configuration writes during carrier/hardware outages.
2. **Deep Inspection:** Verifies Phase 2 Proxy-IDs and compares the active Remote Gateway against the NetBox Single Source of Truth (SSoT).
3. **Traffic Heuristics:** Detects silent "zombie" tunnels by analyzing real-time ingress/egress byte counters.
4. **Deterministic Remediation:** Triggers automated recovery via FortiOS REST API & Python/Netmiko (SSH), logging the full incident lifecycle to MongoDB.

---

## 🔬 Chaos Engineering Matrix & MTTR Benchmarks

A full suite of **24 Chaos Engineering scenarios** was executed to validate system determinism under adverse network conditions:

| Domain | Injected Fault Example | Remediation Strategy | Manual Baseline | Auto MTTR | Delta |
|:---|:---|:---|:---|:---|:---|
| **Overlay IPsec** | Phase 2 SA abrupt tear-down | Automated IKE SA renegotiation | ~18 min | **4.2 s** | `-99.6%` |
| **Underlay Routing** | BGP peer flap damping penalty | Route un-dampen & neighbor clear | ~20 min | **5.8 s** | `-99.5%` |
| **API Failure** | Firewall drop on REST port 8443 | Automatic trigger of Netmiko CLI | ~15 min | **6.9 s** | `-99.2%` |
| **SSoT Drift** | Unauthorized VLAN / IP drift | Force reconcile from NetBox SSoT | ~30 min | **5.1 s** | `-99.7%` |

👉 *Full scenario catalog and execution reports available in [docs/chaos_scenarios.md](docs/chaos_scenarios.md).*

---

## 📊 SRE Observability & Forensic Audit Trail

Every remediation event generates an immutable record stored in **MongoDB**, providing a verifiable audit trail for post-mortems and compliance:

```json
{
  "incident_id": "INC-CHAOS-001",
  "action": "REMEDIATION_REST_API",
  "status": "RESOLVED",
  "duration_seconds": 4.12,
  "timestamp": "2026-09-21T17:13:38.120Z",
  "details": {
    "method_used": "REST_API",
    "api_endpoint": "vpn.ipsec/phase2-interface/tunnel_to_spoke",
    "contingency_invoked": false,
    "netbox_ssot_reconciled": true
  }
}
```

---

## 🚀 Getting Started

### Prerequisites
* Docker & Docker Compose
* Python 3.11+
* Network access to FortiGate (virtual or physical) & NetBox instance

### Setup & Local Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RafaCr3z/netdevops-closed-loop-platform.git
   cd netdevops-closed-loop-platform
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Populate .env with your FortiOS, NetBox, and Webhook tokens
   ```

3. **Spin up data & orchestration services:**
   ```bash
   docker compose up -d
   ```
   *Services initialized:*
   - **n8n Orchestrator:** `http://localhost:5678`
   - **Metabase Analytics:** `http://localhost:3000`
   - **MongoDB Ledger:** `localhost:27017`

4. **Install Python dependencies (PEP 668 compliant):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   pip install -r scripts/requirements.txt
   ```

5. **Execute Chaos Engineering Simulation:**
   ```bash
   python scripts/chaos_injector.py
   ```

---

## 📂 Repository Structure

```text
netdevops-closed-loop-platform/
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI Pipeline: Flake8, Black, Syntax Validation
├── docker-compose.yml             # Containerized Stack (MongoDB, Metabase, n8n)
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
├── README.md                      # Project documentation
│
├── n8n/                           # Orchestration state machine exports
│   └── closed_loop_orchestration.json
│
├── scripts/                       # PEP 668 compliant automation scripts
│   ├── requirements.txt           # Python dependencies
│   ├── fortios_remediation.py     # Primary REST + Fallback Netmiko engine
│   └── chaos_injector.py          # 24-scenario Chaos Engineering runner
│
└── docs/                          # Architecture & test reports
    ├── network_topology.svg       # Laboratory testbed topology diagram
    ├── closed_loop_flow.svg       # Autonomic MAPE-K state machine diagram
    ├── chaos_scenarios.md         # Detailed scenario matrix & benchmarks
    └── chaos_audit_report.json    # Machine-readable test execution report
```

---

## 👥 Authors & Acknowledgments

* **Rafael Cruz** — [LinkedIn](https://linkedin.com/in/rafael-cruz-7159092b2) | [GitHub](https://github.com/RafaCr3z)
* **Institutional Partner:** ARTE, I.P. (*Agência para a Reforma Tecnológica do Estado*)
* **Academic Supervisors:** Prof. Doutor Vasco Soares & Prof. Doutor Alexandre Fonte (*Instituto Politécnico de Castelo Branco - IPCB*)

---
<p align="center">
  <sub>Developed with engineering rigor for mission-critical network automation.</sub>
</p>
