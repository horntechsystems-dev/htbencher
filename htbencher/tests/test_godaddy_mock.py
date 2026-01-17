import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock frappe module
frappe_mock = MagicMock()
sys.modules['frappe'] = frappe_mock
sys.modules['frappe.model.document'] = MagicMock()
sys.modules['frappe.model.document'].Document = object # Mock Document class

# Now we can import the modules to test
# We need to make sure the import path is correct
# Assuming running from apps/htbencher
import os
sys.path.append(os.getcwd())

# Import the client - this will use the mocked frappe
from htbencher.custom import godaddy_client

class TestGoDaddyClient(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        frappe_mock.reset_mock()
        
        # Setup common mocks
        self.root_domain_mock = MagicMock()
        self.root_domain_mock.domain_name = "test.com"
        self.root_domain_mock.get_api_base_url.return_value = "https://api.ote.com"
        self.root_domain_mock.get_auth_header.return_value = "auth-header"
        self.root_domain_mock.default_ttl = 600
        self.root_domain_mock.is_active = 1
        
        frappe_mock.get_doc.return_value = self.root_domain_mock

    @patch('requests.put')
    def test_update_subdomain(self, mock_put):
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {}

        success, msg = godaddy_client.update_subdomain("root_doc", "sub", "1.2.3.4")
        
        self.assertTrue(success)
        mock_put.assert_called_once()
        args, kwargs = mock_put.call_args
        self.assertIn("/v1/domains/test.com/records/A/sub", args[0])
        self.assertEqual(kwargs['json'][0]['data'], "1.2.3.4")

    @patch('requests.get')
    def test_check_availability(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"available": True}

        result = godaddy_client.check_domain_availability("root_doc", "newdomain.com")
        
        self.assertEqual(result['available'], True)
        mock_get.assert_called_once()
        # access call args directly
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['domain'], "newdomain.com")

    @patch('requests.delete')
    def test_delete_subdomain(self, mock_delete):
        mock_delete.return_value.status_code = 204
        
        success, msg = godaddy_client.delete_subdomain("root_doc", "sub")
        
        self.assertTrue(success)
        mock_delete.assert_called_once()
        args, kwargs = mock_delete.call_args
        self.assertIn("/v1/domains/test.com/records/A/sub", args[0])

# We can also test the Site logic by manually invoking the logic, 
# but testing the client functions gives high confidence since the Site logic 
# just calls these. To test Site logic we'd need to mock HTSite class properly 
# which is harder with the import structure. 

if __name__ == "__main__":
    unittest.main()
