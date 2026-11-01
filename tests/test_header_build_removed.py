from pathlib import Path
from html.parser import HTMLParser
import unittest
ROOT=Path(__file__).resolve().parents[1]/'chatify/web'
class Nav(HTMLParser):
    def __init__(self):super().__init__();self.depth=0;self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='nav':self.depth+=1
        if self.depth and tag=='a':self.links.append(a.get('href'))
    def handle_endtag(self,tag):
        if tag=='nav':self.depth-=1
class HeaderBuildRemoved(unittest.TestCase):
    pass
def no_build(name):
    def test(self):
        parser=Nav();parser.feed((ROOT/(name+'.html')).read_text());self.assertNotIn('/build.html',parser.links)
    return test
def other_routes(name):
    def test(self):
        parser=Nav();parser.feed((ROOT/(name+'.html')).read_text())
        for route in ['/','/about.html','/settings.html','/run-locally.html']:self.assertIn(route,parser.links)
    return test
for name in ['index','about','build','run-locally','settings']:
    setattr(HeaderBuildRemoved,'test_no_header_build_'+name.replace('-','_'),no_build(name))
    setattr(HeaderBuildRemoved,'test_other_routes_'+name.replace('-','_'),other_routes(name))
class BuildFunctionPreserved(unittest.TestCase):
    def test_build_page_kept(self):self.assertIn('App creation steps',(ROOT/'build.html').read_text())
    def test_configuration_build_kept(self):self.assertIn('Build with AI',(ROOT/'settingstop.js').read_text())
