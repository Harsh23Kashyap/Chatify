"""Committed-gain regression; measurements are a one-time ffmpeg audit, not listening approval."""
import hashlib,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class StoryGainNormalization(unittest.TestCase):
 def test_manifest_selects_only_verified_gains_and_preserves_originals(self):
  audit=json.loads((ROOT/'docs/story-gain-normalization-20261110.json').read_text())
  manifest=json.loads((ROOT/'chatify/web/media/stories/manifest.json').read_text())['stories']
  self.assertEqual(len(manifest),60)
  gains={r['id']:r for r in audit['verification']};self.assertEqual(len(gains),30)
  for r in manifest:
   original=ROOT/'chatify/web/media/stories'/f"{r['id']}.mp4"
   self.assertTrue(original.is_file())
   if r['id'] not in gains:
    self.assertEqual(r['src'],original.name);continue
   g=gains[r['id']];self.assertEqual(r['src'],g['normalized'])
   self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),g['original_sha256'])
   normalized=original.with_name(r['src'])
   self.assertEqual(hashlib.sha256(normalized.read_bytes()).hexdigest(),g['normalized_sha256'])
   self.assertLessEqual(abs(float(g['after']['input_i'])+24),.25)
   self.assertLessEqual(float(g['after']['input_tp']),-2)
   self.assertGreater(g['gain_db'],0);self.assertTrue(g['video_packet_hash_identical'])
   self.assertEqual(g['subjective_listening'],'NOT REVIEWED')
  for id in ['mouse-mic','hedgehog-prompt','llama-local','elephant-memory','duck-temporary','chameleon-palette','ant-fallback','panda-export']:
   self.assertNotIn(id,gains)
