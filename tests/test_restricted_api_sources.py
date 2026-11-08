import copy,json,unittest
from chatify import buildjobs,schema,generators
BRIEF='Build Paper Trail. Use only the supported Crossref and arXiv connectors, both public no-key metadata APIs. Do not add OpenAlex, paid search, custom HTTP endpoints, Python connectors or other services.'
class RestrictedApiSources(unittest.TestCase):
 def test_exact_observed_brief(self):self.assertEqual(buildjobs.restricted_api_sources(BRIEF),['crossref','arxiv'])
 def test_public_three(self):self.assertEqual(buildjobs.restricted_api_sources('Use only public PubMed, Crossref and arXiv sources.'),['pubmed','crossref','arxiv'])
 def test_single_existing_grammar(self):self.assertEqual(buildjobs.restricted_api_sources('Use only the public PubMed built-in source.'),['pubmed'])
 def test_mentions_are_not_restrictions(self):
  for text in ['Crossref and arXiv research','Use Crossref and arXiv connectors','Only RAG papers','Do not use only Crossref and arXiv connectors','Example: "Use only Crossref and arXiv connectors"']:
   self.assertEqual(buildjobs.restricted_api_sources(text),[])
 def test_unknown_duplicate_ambiguous_lists_rejected(self):
  for text in ['Use only Crossref and Other sources.','Use only Crossref and Crossref sources.','Use only Crossref or arXiv connectors.','Use only Crossref and arXiv connectors. Use only PubMed and Wikipedia sources.']:
   self.assertEqual(buildjobs.restricted_api_sources(text),[])
 def test_trailing_source_directive_not_silently_dropped(self):
  for text in ['Use only Crossref and arXiv connectors, and also PubMed',
               'Use only Crossref and arXiv connectors plus PubMed.',
               'Use only Crossref and arXiv connectors, including PubMed.',
               'Use only Crossref and arXiv connectors but add PubMed.',
               'Use only Crossref and arXiv connectors with PubMed.',
               'Use only Crossref and arXiv connectors, except arXiv.',
               'Use only Crossref and arXiv connectors, PubMed.',
               'Use only Crossref and arXiv connectors - PubMed too.']:
   self.assertEqual(buildjobs.restricted_api_sources(text),[])
 def run_api(self,connectors,selected=None):
  rows=[{'name':c,'service':c,'what':'This service provides searchable published information for research questions.','reason':'This service helps answer the specific research questions in this application.','connector':c,'setup':'Review documentation','caveat':'External details unverified','helper':{'brief':'Inert helper','code':generators.code_template('search','')}} for c in connectors]
  class Provider:
   def complete(self,messages):self.messages=messages;return json.dumps(rows)
  provider=Provider();job={'cancel':False,'calls':0,'provider':provider,'cfg':copy.deepcopy(schema.DEFAULTS),'parts':{},'errors':{},'active':set(),'brief':BRIEF,'confirmed_sources':selected or []}
  buildjobs.BuildJobs()._draft_part(job,'api',dict(buildjobs.PARTS)['api']);return job,provider
 def test_observed_two_source_output_now_accepted(self):
  job,p=self.run_api(['crossref','arxiv']);self.assertEqual(len(job['parts']['api']),2);self.assertIn('overrides the open-ended',p.messages[0]['content'])
 def test_forbidden_extra_rejected(self):
  with self.assertRaisesRegex(ValueError,'confirmed sources'):self.run_api(['crossref','arxiv','openalex'])
 def test_missing_source_rejected(self):
  with self.assertRaisesRegex(ValueError,'confirmed sources'):self.run_api(['crossref'])
 def test_duplicate_source_rejected(self):
  with self.assertRaisesRegex(ValueError,'confirmed sources'):self.run_api(['crossref','crossref'])
 def test_checkbox_contract_remains_authoritative(self):
  job,p=self.run_api(['pubmed'],['pubmed']);self.assertEqual(job['parts']['api'][0]['connector'],'pubmed')
