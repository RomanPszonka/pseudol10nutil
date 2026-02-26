import unittest
import io
import json

from examples.webapp.app import app, ui_base_url, api_base_url
from src.pseudol10nutil.pseudol10nutil import PseudoL10nUtil
from src.pseudol10nutil import transforms as xforms


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Keep util if other tests directly use its methods,
        # or for comparing results in API tests.
        self.util = PseudoL10nUtil()
        # Default transforms for PO file for assertion comparison
        # This should match the defaults set in app.py's po_upload route
        self.util.transforms = [
            xforms.transliterate_diacritic,
            xforms.pad_length,
            xforms.square_brackets
        ]

    def test_pseudo_api(self):
        data = {
            "key1": "The quick brown fox jumps over the lazy dog.",
            "key2": "The quick brown {animal1} jumps over the lazy {animal2}.",
            "key3": "The quick brown %s jumps over the lazy %s.",
            "key4": "The quick brown %(animal1)s jumps over the lazy %(animal2)s.",
        }
        request_data = {"strings": data}
        # Reset transforms to default for this specific API test if needed,
        # as self.util might be configured with PO file defaults in setUp.
        # For this test, we use a fresh PseudoL10nUtil instance with its own default transforms.
        fresh_util_for_api_test = PseudoL10nUtil()
        # If the main API also uses specific non-default transforms, set them here for fresh_util_for_api_test
        # For now, assuming it uses the class defaults.

        resp = self.client.post(
            api_base_url + "pseudo",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            data=json.dumps(request_data),
        )
        self.assertEqual(resp.status_code, 200)
        results = resp.get_json()["strings"]
        for k, v in results.items():
            self.assertEqual(fresh_util_for_api_test.pseudolocalize(data[k]), v)

    def test_po_file_upload_success(self):
        po_content = 'msgid "Hello"\nmsgstr ""'
        # Apply the specific transforms to "Hello" to get the expected output part
        # The self.util is already configured with these transforms in setUp
        expected_output_part = self.util.pseudolocalize("Hello")

        data = {
            'po_file': (io.BytesIO(po_content.encode('utf-8')), 'test.po')
        }
        resp = self.client.post(
            ui_base_url + "po_upload",
            content_type='multipart/form-data',
            data=data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('attachment', resp.headers['Content-Disposition'])
        self.assertIn('filename=pseudolocalized.po', resp.headers['Content-Disposition'])
        # Check if the pseudolocalized string is in the output
        # The actual PO file will have more structure (headers, etc.)
        # but checking for the transformed msgid is a good indicator.
        self.assertIn(expected_output_part, resp.data.decode('utf-8'))


    def test_po_file_upload_no_file(self):
        resp = self.client.post(
            ui_base_url + "po_upload",
            content_type='multipart/form-data',
            data={}
        )
        self.assertEqual(resp.status_code, 400)
        json_data = resp.get_json()
        self.assertIn("error", json_data)
        self.assertIn("No file part", json_data["error"])

    def test_po_file_upload_wrong_file_type(self):
        data = {
            'po_file': (io.BytesIO(b"this is not a po file"), 'test.txt')
        }
        resp = self.client.post(
            ui_base_url + "po_upload",
            content_type='multipart/form-data',
            data=data
        )
        self.assertEqual(resp.status_code, 400)
        json_data = resp.get_json()
        self.assertIn("error", json_data)
        self.assertIn("Invalid file type", json_data["error"])

    def test_po_file_upload_empty_filename(self):
        data = {
            'po_file': (io.BytesIO(b"some content"), '') # Empty filename
        }
        resp = self.client.post(
            ui_base_url + "po_upload",
            content_type='multipart/form-data',
            data=data
        )
        self.assertEqual(resp.status_code, 400)
        json_data = resp.get_json()
        self.assertIn("error", json_data)
        self.assertIn("No file selected", json_data["error"])


if __name__ == "__main__":
    unittest.main()
