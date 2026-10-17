import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch

class ConfigLockNames(unittest.TestCase):
    def test_new_and_legacy_names(self):
        tree=ast.parse((Path(__file__).parents[1]/'chatify/server.py').read_text())
        node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LOCKED' for t in n.targets))
        code=compile(ast.Expression(node.value),'<lock>','eval')
        for name in ['CHATIFY_CONFIG','CUSTOMCHAT_CONFIG']:
            for value,want in [('on',False),('off',True),(' OFF ',True),('1',False),('',False)]:
                with self.subTest(name=name,value=value),patch.dict(os.environ,{name:value},clear=True):
                    self.assertIs(eval(code,{'os':os}),want)
