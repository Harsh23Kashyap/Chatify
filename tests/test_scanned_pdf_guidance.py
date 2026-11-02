import pathlib,unittest
from unittest.mock import patch
from chatify import pdfread,schema
class ScannedPDFGuidance(unittest.TestCase):
 def test_scan_failure_no_success_claim_or_automatic_ocr(self):
  with patch('pypdf.PdfReader',side_effect=ValueError('scan')),patch.object(pdfread,'_builtin',return_value=''),patch.object(pdfread,'_ocr_page',side_effect=AssertionError('must not OCR')):
   with self.assertRaisesRegex(ValueError,'This upload was not added.*explicit local OCR'):pdfread.extract(b'%PDF scanfixture')
 def test_explicit_connector_choice_default_off(self):
  from chatify.connectors.local_files import LocalFiles
  import tempfile
  with tempfile.TemporaryDirectory()as d:
   self.assertFalse(LocalFiles({'id':'docs','label':'Docs','type':'local_files','path':d}).ocr)
  cfg=schema.validate({'sources':[{'id':'docs','type':'local_files','path':'docs','ocr':True}]});self.assertTrue(cfg['sources'][0]['ocr'])
 def test_help_keeps_page_original_and_uncertainty_visible(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text()
  for text in ['Scanned PDF: local OCR option','This file was not added.','No external OCR service is used.','original document name, file version, page number and OCR label','OCR can misread words and clause numbers','Example only, not applied.']:
   self.assertIn(text,js)
