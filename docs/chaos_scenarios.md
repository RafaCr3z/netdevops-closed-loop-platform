# 🔬 Extended Synthetic Chaos Taxonomy (Offline Telemetry Demonstrator)

> [!IMPORTANT]
> **Methodology & Evidence Distinction (Empirical Lab vs. Offline Simulation):**  
> - **Verified Empirical Laboratory Validation (10 Scenarios A–J · 24 Recorded Incidents):** Live network fault injections were executed in **VMware Workstation Pro (`FortiOS v7.6.4`)** across 10 scenarios (**A–E** in Phase 1 SSH/Netmiko and **F–J** in Phase 2 Native REST API CMDB), producing **24 audited MongoDB records**:
>   - **Phase 1 (`incident_runs` — 13 incidents):** **7 / 7 eligible logical faults** (`rgwy_mismatch`, `phase2_mismatch`, `zero_traffic`) verified as `auto_recovered` (4.0s–7.0s FortiOS syslog convergence), **4 WAN MPLS cuts** (`mpls_down`) escalated via SMTP Mailtrap (`escalated_to_provider`), and **2 branch power blackouts** (`power_or_hardware_failure`) safely aborted via ICMP Pre-Check (`not_attempted`).
>   - **Phase 2 (`incident_runs_enterprise` — 11 incidents):** **8 / 8 eligible logical faults** (`rgwy_mismatch`, `phase2_mismatch`, `policy_disabled`) verified as `Success` / `auto_recovered` via native FortiOS REST API CMDB `HTTP PUT` (< 2s), and **3 physical/WAN faults** (`2` `power_or_hardware_failure`, `1` `mpls_down`) safely aborted (`not_attempted`).
>   - 👉 Full methodology, FortiOS v7.6.4 syslogs, and photographic evidence: [**`docs/empirical_lab_validation.md`**](empirical_lab_validation.md).
> - **Offline Synthetic Demonstrator (`scripts/chaos_simulation_demo.py`):** The 24-entry table below specifies an **extended synthetic taxonomy** used by [`scripts/chaos_simulation_demo.py`](../scripts/chaos_simulation_demo.py) to generate simulated telemetry (`SIMULATED_RECOVERED`) for local Docker evaluation (`MongoDB` + `Metabase`) when commercial FortiGate VMs are not present. **Values in the table below are simulated projections parameterized from lab baselines, not verified hardware recoveries.**

## 📋 Extended Synthetic Taxonomy Matrix (`scripts/chaos_simulation_demo.py`)

| ID | Domain | Scenario Name | Simulated Fault | Modeled Remediation Strategy | Assumed Manual Baseline | Simulated Auto Latency | Simulated Delta |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **01** | Overlay IPsec | Phase 2 Tunnel Drop | Abrupt SA tear-down | Re-initiate IKE Phase 2 SA via API | 18.0 min | **4.2 s** (sim) | -99.6% |
| **02** | Overlay IPsec | Phase 1 Rekey Mismatch | Lifetime disparity in IKE proposal | Align lifetime params to NetBox SSoT | 25.0 min | **4.8 s** (sim) | -99.7% |
| **03** | Overlay IPsec | DPD Timeout | Packet drop on keepalive | Trigger DPD reset & route failover | 15.0 min | **5.1 s** (sim) | -99.4% |
| **04** | Overlay IPsec | Encryption Proposal Drift | Desync cipher AES-256 to AES-128 | Patch CMDB IPsec profile | 30.0 min | **4.5 s** (sim) | -99.7% |
| **05** | Overlay IPsec | Interface MTU Blackhole | MTU clamped below MSS threshold | Restore 1420 MTU clamp standard | 22.0 min | **4.3 s** (sim) | -99.7% |
| **06** | Overlay IPsec | Secondary Tunnel Failover | Primary gateway unreachable | Switch BGP metric to backup tunnel | 14.0 min | **5.4 s** (sim) | -99.4% |
| **07** | Underlay MPLS | BGP Peer Flapping | Route flap damping penalty | Clear BGP neighbor & dampen damping | 20.0 min | **5.8 s** (sim) | -99.5% |
| **08** | Underlay MPLS | MPLS Label Swapping Drop | Null-route on MPLS core egress | Reroute telemetry via IPsec overlay | 35.0 min | **6.2 s** (sim) | -99.7% |
| **09** | Underlay MPLS | Default Route Blackhole | Missing static 0.0.0.0/0 gateway | Inject default route via FortiOS API | 15.0 min | **4.1 s** (sim) | -99.5% |
| **10** | Underlay MPLS | Jitter / Latency Spike | Injected latency > 250ms | Dynamic SLA steering to VPN path | 18.0 min | **5.0 s** (sim) | -99.5% |
| **11** | Underlay MPLS | OSPF Adjacency Loss | Hello timer mismatch | Sync OSPF timers with NetBox | 24.0 min | **4.9 s** (sim) | -99.7% |
| **12** | Underlay MPLS | WAN CRC Error Flood | Interface error rate threshold | Disable flapping port and failover | 28.0 min | **6.5 s** (sim) | -99.6% |
| **13** | API & Contingency | REST API HTTPS Block | Firewall drop on REST port 8443 | Trigger Netmiko SSH fallback CLI | 15.0 min | **6.9 s** (sim) | -99.2% |
| **14** | API & Contingency | REST Token Expiry | Expired Bearer token (HTTP 401) | Renew token & retry fallback | 12.0 min | **6.4 s** (sim) | -99.1% |
| **15** | API & Contingency | CMDB Lock Contention | Concurrent write collision (423) | Exponential backoff retry patch | 10.0 min | **5.2 s** (sim) | -99.1% |
| **16** | API & Contingency | SSL Cert Verification Fail | Expired certificate authority | Switch to trusted SSH channel | 20.0 min | **6.7 s** (sim) | -99.4% |
| **17** | API & Contingency | Rate Limiting (HTTP 429) | API burst rate exceeded | Queue and rate-throttle remediation | 15.0 min | **5.9 s** (sim) | -99.3% |
| **18** | API & Contingency | VDOM Memory Pressure | Memory allocation > 90% | Purge stale diagnostic sessions | 30.0 min | **7.1 s** (sim) | -99.6% |
| **19** | SSoT Drift | IPAM Subnet Desync | Manual unauthorized IP change | Force reconcile from NetBox SSoT | 30.0 min | **5.1 s** (sim) | -99.7% |
| **20** | SSoT Drift | VLAN Configuration Drift | VLAN ID changed to 999 | Restore canonical VLAN from NetBox | 25.0 min | **4.6 s** (sim) | -99.7% |
| **21** | SSoT Drift | Firewall Policy Rule Desync | Missing outbound rule | Re-inject FortiOS firewall policy | 40.0 min | **5.3 s** (sim) | -99.8% |
| **22** | SSoT Drift | SNMP Community Drift | Corrupted monitoring secret | Sync SNMP string with PRTG vault | 20.0 min | **4.4 s** (sim) | -99.6% |
| **23** | SSoT Drift | DNS Forwarder Desync | Invalid internal resolver | Restore corporate DNS resolvers | 18.0 min | **4.2 s** (sim) | -99.6% |
| **24** | SSoT Drift | NTP Server Time Offset | NTP offset > 5000ms | Force NTP resync with ARTE server | 15.0 min | **4.0 s** (sim) | -99.6% |

---

## 📊 Simulated Output Summary vs. Verified Empirical Results
- **Offline Simulator Output (`scripts/chaos_simulation_demo.py`):** Generates `24 / 24` synthetic telemetry records tagged as `"status": "SIMULATED_RECOVERED"` (modeled mean latency: `5.2s` with $\pm 0.25\text{s}$ jitter vs. `21.4 min` assumed manual baseline) to populate local MongoDB/Metabase dashboards without live appliances.
- **Verified Empirical Lab Results ([`docs/empirical_lab_validation.md`](empirical_lab_validation.md)):** Across **24 real fault-injection runs** in VMware Workstation Pro (`FortiOS v7.6.4`), **15 / 15 eligible logical faults** (`7` in Phase 1 SSH/Netmiko + `8` in Phase 2 REST API CMDB) achieved verified autonomous tunnel/policy recovery (**4.0s–7.0s** syslog convergence), while **9 / 24 physical or external faults** (`5` `mpls_down` + `4` `power_or_hardware_failure`) were accurately isolated and escalated/aborted (`not_attempted` / `escalated_to_provider`) without issuing futile configuration writes.

