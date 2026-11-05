import copy,json,unittest
from pathlib import Path
from maintain import ROOT,validate,check_coverage,canonical
class LibraryTests(unittest.TestCase):
 def setUp(self):self.d=json.loads((ROOT/'library.json').read_text())
 def bad(self,fn):
  fn(self.d)
  with self.assertRaises(ValueError):validate(self.d)
 def test_real_library(self):self.assertEqual(validate(self.d),{'entries':44,'ready':44,'images':132})
 def test_coverage(self):self.assertTrue(check_coverage(self.d,json.loads((ROOT/'source-capture/catalog-snapshot.json').read_text())))
 def test_duplicate_id(self):self.bad(lambda d:d['entries'].append(copy.deepcopy(d['entries'][0])))
 def test_duplicate_source(self):
  e=copy.deepcopy(self.d['entries'][0]);e['id']='different';e['source_url']+='#section';self.d['entries'].append(e)
  with self.assertRaises(ValueError):validate(self.d)
 def test_new_draft(self):
  e=copy.deepcopy(self.d['entries'][0]);e.update(id='studio-new',source_url='https://example.com/reference',status='DRAFT');self.d['entries'].append(e)
  self.assertEqual(validate(self.d)['entries'],45)
  self.assertTrue(check_coverage(self.d,json.loads((ROOT/'source-capture/catalog-snapshot.json').read_text())))
 def test_missing_image(self):self.bad(lambda d:d['entries'][0]['media'][0].update(file='images/missing.webp'))
 def test_changed_hash(self):self.bad(lambda d:d['entries'][0]['media'][0].update(sha256='bad'))
 def test_escape_path(self):self.bad(lambda d:d['entries'][0]['media'][0].update(file='../outside.webp'))
 def test_missing_credit(self):self.bad(lambda d:d['entries'][0]['media'][0].update(credit=''))
 def test_invalid_status(self):self.bad(lambda d:d['entries'][0].update(status='APPROVED'))
 def test_version(self):self.bad(lambda d:d['entries'][0].update(version=0))
 def test_duplicate_image(self):self.bad(lambda d:d['entries'][0]['media'].append(copy.deepcopy(d['entries'][0]['media'][0])))
 def test_representative_mismatch(self):self.bad(lambda d:d['entries'][0].update(image='images/other.webp'))
 def test_missing_catalog_entry(self):
  self.d['entries'].pop()
  with self.assertRaises(ValueError):check_coverage(self.d,json.loads((ROOT/'source-capture/catalog-snapshot.json').read_text()))
 def test_missing_gallery_image(self):
  self.d['entries'][0]['media'].pop()
  with self.assertRaises(ValueError):check_coverage(self.d,json.loads((ROOT/'source-capture/catalog-snapshot.json').read_text()))
 def test_cloud_links_required(self):
  self.d['entries'][0]['media'][0].pop('drive_url',None)
  with self.assertRaises(ValueError):validate(self.d,require_cloud=True)
 def test_url_query_preserved(self):self.assertNotEqual(canonical('https://example.com/a?v=1'),canonical('https://example.com/a?v=2'))
if __name__=='__main__':unittest.main()
