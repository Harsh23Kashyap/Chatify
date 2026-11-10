"""Paper-reading scope is not a request for a full-length response.

First two strings are frozen actual Nov8 request/standalone text. Other cases
are synthetic controls. Prompt checks are not live model-quality evidence.
"""
import unittest
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine, concise_request
from chatify.store import Store

RAW = 'Explain the previous answer more simply using the same sources. Keep the source links and distinguish returned metadata from full-paper reading.'
STANDALONE = 'Explain the previous answer in simpler terms using the same sources. Keep the source links and make clear what comes from returned metadata versus full-paper reading.'

class FullPaperSimplificationIntent(unittest.TestCase):
    def test_paper_scope_does_not_cancel_simplification(self):
        for q in (RAW, STANDALONE,
                  'Explain more simply without claiming full paper reading.',
                  'Explain more simply and distinguish metadata from full papers.',
                  'Explain more simply and distinguish metadata from full-paper access.'):
            with self.subTest(q=q):self.assertTrue(concise_request(q))

    def test_typographic_paper_hyphens_keep_same_intent(self):
        for hyphen in ('-', '\u2010', '\u2011'):
            q=RAW.replace('full-paper', 'full'+hyphen+'paper')
            with self.subTest(hyphen=hyphen):
                self.assertTrue(concise_request(q))
                self.assertFalse(concise_request(q+' Give a full answer.'))
                self.assertFalse(concise_request(q,'deep'))
                self.assertFalse(concise_request(q+' Use exactly 300 words.'))

    def test_explicit_detail_depth_and_word_count_preserved(self):
        for q,style in ((RAW+' Give a full answer.','standard'),
                        (RAW+' Explain in detail.','standard'),
                        (RAW+' Give a fuller explanation.','standard'),
                        (RAW,'deep'),(RAW+' Use exactly 300 words.','standard'),
                        ('Compare full-paper reading with reading abstracts.','standard')):
            with self.subTest(q=q,style=style):self.assertFalse(concise_request(q,style))

    def test_frozen_request_and_rewrite_reach_generation_and_revision_prompts(self):
        evidence=[{'n':1,'id':'fixture','source':'docs','title':'Research record',
                   'text':'Research record metadata is available.','url':'fixture:record'}]
        for q in (RAW,STANDALONE):
            with self.subTest(q=q):
                e=Engine(schema.validate({'sources':[]}),Store(':memory:'),connectors={})
                e._llm_on=lambda k:True
                e.provider=Mock();e.provider.complete.return_value='Research record metadata is available. [1]'
                system=e.prompt(q,evidence,'standard',[], '')[0]['content']
                self.assertIn('This is a simplification request',system)
                self.assertIn('at most 120 words',system)
                e.revise('Research record metadata is available. [1]',evidence,q)
                self.assertIn('The reader requested simplification',e.provider.complete.call_args.args[0][0]['content'])
                self.assertIn('at most 120 words',e.provider.complete.call_args.args[0][0]['content'])

if __name__=='__main__':unittest.main()
