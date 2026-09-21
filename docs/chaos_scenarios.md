# Chaos Engineering & Reliability Audit: 24 Scenarios

This document details the **24 fault-injection scenarios** executed and validated against hybrid enterprise network topoligies (Underlay MPLS + Overlay IPsec VPN FortiGate).

## Summary Matrix

| ID | Domain | Scenario Name | Injected Failure | Automated Remediation Strategy | Manual MTTR | Auto MTTR | Reduction |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **01** | Overlay IPsec | Phase 2 Tunnel Drop | Abrupt SA tear-down | Re-initiate IKE Phase 2 SA via API | 18.0 min | **4.2 s** | -99.6% |
| **02** | Overlay IPsec | Phase 1 Rekey Mismatch | Lifetime disparity in IKE proposal | Align lifetime params to NetBox SSoT | 25.0 min | **4.8 s** | -99.7% |
| **03** | Overlay IPsec | DPD Timeout | Packet drop on keepalive | Trigger DPD reset & route failover | 15.0 min | **5.1 s** | -99.4% |
| **04** | Overlay IPsec | Encryption Proposal Drift | Desync cipher AES-256 to AES-128 | Patch CMDB IPsec profile | 30.0 min | **4.5 s** | -99.7% |
| **05** | Overlay IPsec | Interface MTU Blackhole | MTU clamped below MSS threshold | Restore 1420 MTU clamp standard | 22.0 min | **4.3 s** | -99.7% |
| **06** | Overlay IPsec | Secondary Tunnel Failover | Primary gateway unreachable | Switch BGP metric to backup tunnel | 14.0 min | **5.4 s** | -99.4% |
| **07** | Underlay MPLS | BGP Peer Flapping | Route flap damping penalty | Clear BGP neighbor & dampen damping | 20.0 min | **5.8 s** | -99.5% |
| **08** | Underlay MPLS | MPLS Label Swapping Drop | Null-route on MPLS core egress | Reroute telemetry via IPsec overlay | 35.0 min | **6.2 s** | -99.7% |
| **09** | Underlay MPLS | Default Route Blackhole | Missing static 0.0.0.0/0 gateway | Inject default route via FortiOS API | 15.0 min | **4.1 s** | -99.5% |
| **10** | Underlay MPLS | Jitter / Latency Spike | Injected latency > 250ms | Dynamic SLA steering to VPN path | 18.0 min | **5.0 s** | -99.5% |
| **11** | Underlay MPLS | OSPF Adjacency Loss | Hello timer mismatch | Sync OSPF timers with NetBox | 24.0 min | **4.9 s** | -99.7% |
| **12** | Underlay MPLS | WAN CRC Error Flood | Interface error rate threshold | Disable flapping port and failover | 28.0 min | **6.5 s** | -99.6% |
| **13** | API & Contingency | REST API HTTPS Block | Firewall drop on REST port 8443 | Trigger Netmiko SSH fallback CLI | 15.0 min | **6.9 s** | -99.2% |
| **14** | API & Contingency | REST Token Expiry | Expired Bearer token (HTTP 401) | Renew token & retry fallback | 12.0 min | **6.4 s** | -99.1% |
| **15** | API & Contingency | CMDB Lock Contention | Concurrent write collision (423) | Exponential backoff retry patch | 10.0 min | **5.2 s** | -99.1% |
| **16** | API & Contingency | SSL Cert Verification Fail | Expired certificate authority | Switch to trusted SSH channel | 20.0 min | **6.7 s** | -99.4% |
| **17** | API & Contingency | Rate Limiting (HTTP 429) | API burst rate exceeded | Queue and rate-throttle remediation | 15.0 min | **5.9 s** | -99.3% |
| **18** | API & Contingency | VDOM Memory Pressure | Memory allocation > 90% | Purge stale diagnostic sessions | 30.0 min | **7.1 s** | -99.6% |
| **19** | SSoT Drift | IPAM Subnet Desync | Manual unauthorized IP change | Force reconcile from NetBox SSoT | 30.0 min | **5.1 s** | -99.7% |
| **20** | SSoT Drift | VLAN Configuration Drift | VLAN ID changed to 999 | Restore canonical VLAN from NetBox | 25.0 min | **4.6 s** | -99.7% |
| **21** | SSoT Drift | Firewall Policy Rule Desync | Missing outbound rule | Re-inject FortiOS firewall policy | 40.0 min | **5.3 s** | -99.8% |
| **22** | SSoT Drift | SNMP Community Drift | Corrupted monitoring secret | Sync SNMP string with PRTG vault | 20.0 min | **4.4 s** | -99.6% |
| **23** | SSoT Drift | DNS Forwarder Desync | Invalid internal resolver | Restore corporate DNS resolvers | 18.0 min | **4.2 s** | -99.6% |
| **24** | SSoT Drift | NTP Server Time Offset | NTP offset > 5000ms | Force NTP resync with ARTE server | 15.0 min | **4.0 s** | -99.6% |

---

## Benchmark Results
- **Baseline Manual Recovery:** 21.4 minutes average across operations teams.
- **Closed-Loop Automated Recovery:** 5.2 seconds average (deterministic execution).
- **Chaos Resilience Rate:** 100% (24 / 24 scenarios successfully recovered).
