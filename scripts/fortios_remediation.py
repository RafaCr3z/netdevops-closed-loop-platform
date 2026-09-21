"""
NetDevOps Closed-Loop Active Self-Healing Engine
------------------------------------------------
Primary: Synchronous FortiOS CMDB REST API Patch
Fallback: Python Netmiko CLI/SSH Contingency Engine (PEP 668 Compliant)
Audit Trail: MongoDB Immutability & Event Timings

Author: Rafael Cruz
Partner: ARTE, I.P.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
import requests
import urllib3
from dotenv import load_dotenv
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from pymongo import MongoClient

# Disable insecure HTTPS warnings for self-signed FortiGate certificates in lab environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment configuration
load_dotenv()

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
)
logger = logging.getLogger("NetDevOps-Remediation")


class FortiOSRemediationEngine:
    def __init__(self):
        self.host = os.getenv("FORTIGATE_HOST", "127.0.0.1")
        self.port = os.getenv("FORTIGATE_REST_PORT", "8443")
        self.api_token = os.getenv("FORTIGATE_API_TOKEN", "")
        self.ssh_user = os.getenv("FORTIGATE_SSH_USER", "admin")
        self.ssh_password = os.getenv("FORTIGATE_SSH_PASSWORD", "")
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/netdevops_audit")
        self.db = self._init_db_connection()

    def _init_db_connection(self):
        """Initializes connection to MongoDB for audit logging."""
        try:
            client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            return client.get_database()
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB audit log: {e}")
            return None

    def log_incident_audit(self, incident_id: str, action: str, status: str, duration_sec: float, details: dict):
        """Records an immutable audit event for MTTR & compliance tracking."""
        record = {
            "incident_id": incident_id,
            "action": action,
            "status": status,
            "duration_seconds": round(duration_sec, 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details
        }
        logger.info(f"Audit Record [MTTR: {duration_sec:.3f}s]: {status} - {action}")
        if self.db is not None:
            try:
                self.db["remediation_audit_trail"].insert_one(record)
            except Exception as e:
                logger.error(f"MongoDB write failed: {e}")
        return record

    def primary_api_remediation(self, endpoint_path: str, payload: dict) -> tuple[bool, str]:
        """
        Executes synchronous PATCH / PUT request to FortiOS REST API CMDB.
        """
        url = f"https://{self.host}:{self.port}/api/v2/cmdb/{endpoint_path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        try:
            logger.info(f"Attempting Primary REST API remediation on: {url}")
            response = requests.put(
                url,
                headers=headers,
                data=json.dumps(payload),
                verify=False,
                timeout=5.0
            )

            if response.status_code in [200, 204]:
                logger.info("Primary REST API remediation succeeded (HTTP 200/204).")
                return True, response.text
            else:
                logger.warning(f"REST API returned non-success status: {response.status_code} - {response.text}")
                return False, f"HTTP_{response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.warning(f"REST API connection error/timeout: {e}")
            return False, str(e)

    def fallback_cli_remediation(self, cli_commands: list[str]) -> tuple[bool, str]:
        """
        Fallback contingency engine using Netmiko (SSH) under PEP 668 isolation.
        """
        logger.info("Initiating Out-of-Band Fallback Remediation via Netmiko SSH...")
        device_params = {
            "device_type": "fortinet",
            "host": self.host,
            "username": self.ssh_user,
            "password": self.ssh_password,
            "timeout": 10,
            "session_log": None
        }

        try:
            with ConnectHandler(**device_params) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(cli_commands)
                logger.info("Fallback SSH configuration applied successfully.")
                return True, output
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            logger.critical(f"Fallback SSH connection failed: {e}")
            return False, str(e)
        except Exception as e:
            logger.critical(f"Unexpected error in fallback execution: {e}")
            return False, str(e)

    def execute_remediation(self, incident_id: str, api_endpoint: str, api_payload: dict, fallback_cli: list[str]) -> dict:
        """
        Orchestrates hybrid execution: Primary REST API -> Fallback Netmiko -> Audit Trail.
        """
        start_time = time.time()
        method_used = "REST_API"

        # 1. Primary Attempt
        success, response_msg = self.primary_api_remediation(api_endpoint, api_payload)

        # 2. Fallback Contingency if Primary Failed
        if not success:
            logger.warning("Primary REST API failed. Triggering out-of-band Netmiko contingency engine...")
            method_used = "NETMIKO_SSH_FALLBACK"
            success, response_msg = self.fallback_cli_remediation(fallback_cli)

        duration = time.time() - start_time
        status = "RESOLVED" if success else "FAILED"

        audit_result = self.log_incident_audit(
            incident_id=incident_id,
            action=f"REMEDIATION_{method_used}",
            status=status,
            duration_sec=duration,
            details={
                "method_used": method_used,
                "api_endpoint": api_endpoint,
                "response": response_msg,
                "contingency_invoked": (method_used == "NETMIKO_SSH_FALLBACK")
            }
        )

        return audit_result


if __name__ == "__main__":
    engine = FortiOSRemediationEngine()

    # Mock Scenario: IPsec Phase 2 Tunnel Bounce & Interface Reset
    test_incident_id = f"INC-VPN-{int(time.time())}"
    test_endpoint = "vpn.ipsec/phase2-interface/tunnel_to_hq"
    test_payload = {
        "auto-negotiate": "enable",
        "keepalive": 10
    }
    test_fallback_cmds = [
        "config vpn ipsec phase2-interface",
        "edit tunnel_to_hq",
        "set auto-negotiate enable",
        "set keepalive 10",
        "end"
    ]

    print("\n--- Running Closed-Loop Remediation Engine ---")
    result = engine.execute_remediation(
        incident_id=test_incident_id,
        api_endpoint=test_endpoint,
        api_payload=test_payload,
        fallback_cli=test_fallback_cmds
    )
    print(json.dumps(result, indent=2, default=str))
