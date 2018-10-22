import unittest

from eocdb_client.api.mpf import MultiPartForm
from tests.helpers import ClientTest


class MultiPartFormTest(unittest.TestCase):

    def test_it(self):
        form = MultiPartForm(boundary="bibo")

        form.add_field("path", "BIGELOW/BALCH/gnats")

        file_obj = ClientTest.get_input_path("chl", "chl-s170604w.sub")
        form.add_file("datasetFiles",
                      "chl/chl-s170604w.sub",
                      file_obj)

        file_obj = open(ClientTest.get_input_path("chl", "chl-s170710w.sub"))
        form.add_file("datasetFiles",
                      "chl/chl-s170710w.sub",
                      file_obj)

        binary_form = bytes(form)
        self.assertEqual(4795, len(binary_form))

        text_form = str(form)
        self.assertEqual(4795, len(text_form))
        self.assertTrue(text_form.startswith("--bibo\r\n"))
        self.assertTrue(text_form.endswith("--bibo--\r\n"))
