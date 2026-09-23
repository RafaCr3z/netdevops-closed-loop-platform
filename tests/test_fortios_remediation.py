"""
Unit Tests for NetDevOps Closed-Loop Auto-Remediation Engine
------------------------------------------------------------
Validates:
1. Primary REST API Remediation (HTTP 200/204)
2. Primary API Timeout & Failure triggering Netmiko Out-of-Band SSH Fallback
3. Complete Failure Handling & Audit Log Structure
"""

import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, RequestException
from scripts.fortios_remediation import FortiOSRemediationEngine


class TestFortiOSRemediationEngine(unittest.TestCase):

    def setUp(self):
        """Sets up isolated engine with mocked MongoDB client."""
        with patch("scripts.fortios_remediation.MongoClient") as mock_mongo:
            self.mock_db = MagicMock()
            mock_mongo.return_value.get_database.return_value = self.mock_db
            self.engine = FortiOSRemediationEngine()
            self.engine.db = self.mock_db

    @patch("requests.put")
    def test_primary_api_remediation_success(self, mock_put):
        """Scenario 1: Primary FortiOS REST API succeeds (HTTP 200)."""
        mock_put.return_value.status_code = 200
        mock_put.return_value.text = '{"status": "success", "http_status": 200}'

        result = self.engine.execute_remediation(
            incident_id="INC-TEST-001",
            api_endpoint="vpn.ipsec/phase2-interface/tunnel_to_hq",
            api_payload={"auto-negotiate": "enable"},
            fallback_cli=["config vpn ipsec phase2-interface", "edit tunnel_to_hq", "set auto-negotiate enable", "end"]
        )

        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["details"]["method_used"], "REST_API")
        self.assertFalse(result["details"]["contingency_invoked"])
        self.assertGreaterEqual(result["duration_seconds"], 0)

    @patch("requests.put")
    @patch("scripts.fortios_remediation.ConnectHandler")
    def test_api_timeout_triggers_fallback_ssh_success(self, mock_connect, mock_put):
        """Scenario 2: Primary API times out -> Netmiko SSH Fallback succeeds."""
        mock_put.side_effect = Timeout("Connection to FortiOS timed out")
        mock_ssh_instance = MagicMock()
        mock_ssh_instance.send_config_set.return_value = "Applied fallback CLI configuration."
        mock_connect.return_value.__enter__.return_value = mock_ssh_instance

        result = self.engine.execute_remediation(
            incident_id="INC-TEST-002",
            api_endpoint="vpn.ipsec/phase2-interface/tunnel_to_hq",
            api_payload={"auto-negotiate": "enable"},
            fallback_cli=["config vpn ipsec phase2-interface", "edit tunnel_to_hq", "set auto-negotiate enable", "end"]
        )

        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["details"]["method_used"], "NETMIKO_SSH_FALLBACK")
        self.assertTrue(result["details"]["contingency_invoked"])
        mock_ssh_instance.send_config_set.assert_called_once()

    @patch("requests.put")
    @patch("scripts.fortios_remediation.ConnectHandler")
    def test_both_primary_and_fallback_fail(self, mock_connect, mock_put):
        """Scenario 3: Both REST API and SSH Fallback fail -> Status FAILED with audit."""
        mock_put.side_effect = RequestException("API Network unreachable")
        mock_connect.side_effect = Exception("SSH port closed")

        result = self.engine.execute_remediation(
            incident_id="INC-TEST-003",
            api_endpoint="vpn.ipsec/phase2-interface/tunnel_to_hq",
            api_payload={"auto-negotiate": "enable"},
            fallback_cli=["dummy command"]
        )

        self.assertEqual(result["status"], "FAILED")
        self.assertTrue(result["details"]["contingency_invoked"])


if __name__ == "__main__":
    unittest.main()
