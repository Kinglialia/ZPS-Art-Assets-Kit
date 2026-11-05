import copy, hashlib, importlib.util, json, pathlib, tempfile, unittest
SOURCE=pathlib.Path(__file__).resolve().parent
if not (SOURCE/'maintain.py').is_file():
 SOURCE=pathlib.Path.cwd()/'art-director-reference-library'
spec=importlib.util.spec_from_file_location('review_maintain',SOURCE/'maintain.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BASE=json.loads((SOURCE/'library.json').read_text())
class Regression(unittest.TestCase):
 def rejected(self,change):
  d=copy.deepcopy(BASE);change(d)
  with self.assertRaises(ValueError):m.validate(d)
 def test_draft_name(self):self.rejected(lambda d:(d['entries'][0].update(status='DRAFT'),d['entries'][0].pop('name')))
 def test_media_review_type(self):self.rejected(lambda d:d['entries'][0]['media'][0].update(visual_review=1))
 def test_optional_drive_url_type(self):self.rejected(lambda d:d['entries'][0]['media'][0].update(drive_url=1))
 def test_optional_official_url_type(self):self.rejected(lambda d:d['entries'][0]['media'][0].update(official_url=1))
 def test_baseline(self):self.assertEqual(m.validate(BASE),{'entries':44,'ready':44,'images':132})
 def test_card_escape(self):self.rejected(lambda d:d['entries'][0].update(card='../outside.txt'))
 def test_duplicate_card(self):self.rejected(lambda d:d['entries'][1].update(card=d['entries'][0]['card']))
 def test_dimensions(self):self.rejected(lambda d:d['entries'][0]['media'][0].update(width=1,height=1))
 def test_alias_hash(self):self.rejected(lambda d:d['entries'][0].update(image_sha256='bad'))
 def test_alias_source(self):self.rejected(lambda d:d['entries'][0].update(image_source_url='https://example.com/x'))
 def test_media_review(self):self.rejected(lambda d:d['entries'][0]['media'][0].pop('visual_review'))
 def test_name(self):self.rejected(lambda d:d['entries'][0].pop('name'))
 def test_limitations(self):self.rejected(lambda d:d['entries'][0].pop('limitations'))
 def test_date_format(self):self.rejected(lambda d:d['entries'][0].update(checked_at='not-a-date'))
 def test_date_calendar(self):self.rejected(lambda d:d['entries'][0].update(checked_at='2026-02-30'))
 def test_undecodable_matching_hash(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);(root/'cards').mkdir();(root/'bad.webp').write_bytes(b'not an image')
   d=copy.deepcopy(BASE);d['entries']=d['entries'][:1];e=d['entries'][0];e['media']=e['media'][:1];v=e['media'][0];v.update(file='bad.webp',sha256=hashlib.sha256(b'not an image').hexdigest());e.update(image=v['file'],image_sha256=v['sha256'])
   with self.assertRaises(ValueError):m.validate(d,root=root)
if __name__=='__main__':unittest.main(verbosity=2)
