import importlib.util,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
spec=importlib.util.spec_from_file_location('installer_matrix',Path(__file__).with_name('installer_matrix.py'));matrix=importlib.util.module_from_spec(spec);spec.loader.exec_module(matrix)
class MatrixPortTests(unittest.TestCase):
 def test_real_bound_port_keeps_launcher_fallback_room(self):
  with matrix.occupied_port_socket() as sock:self.assertTrue(20000<=sock.getsockname()[1]<60000)
 def test_busy_candidate_closes_and_retries_bounded_range(self):
  first=MagicMock();first.bind.side_effect=OSError('busy');second=MagicMock()
  with patch.object(matrix.random,'randrange',side_effect=[23456,23457]) as rng,patch.object(matrix.socket,'socket',side_effect=[first,second]):
   self.assertIs(matrix.occupied_port_socket(),second)
  first.close.assert_called_once();second.bind.assert_called_once_with(('127.0.0.1',23457));self.assertEqual(rng.call_count,2)
 def test_exhaustion_is_bounded_and_closes_every_socket(self):
  sock=MagicMock();sock.bind.side_effect=OSError('busy')
  with patch.object(matrix.socket,'socket',return_value=sock),self.assertRaisesRegex(RuntimeError,'Could not reserve'):matrix.occupied_port_socket()
  self.assertEqual(sock.close.call_count,100)
