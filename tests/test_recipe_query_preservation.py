import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('recipe_sources_test', Path(__file__).resolve().parents[1] / 'apps/recipechat/recipe_sources.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

class RecipeNameQueryTests(unittest.TestCase):
    def test_margherita_name_order_and_unrelated_pizza(self):
        seen=[]
        def get(url):
            seen.append(url)
            if url.endswith('s=margherita'):
                return {'meals':[{'idMeal':'1','strMeal':'Pizza Express Margherita','strInstructions':'Make this recipe.'}, {'idMeal':'2','strMeal':'Margherita cocktail','strInstructions':'Mix.'}]}
            return {'meals':[]}
        with patch.object(r,'_get',side_effect=get):
            rows=r.mealdb('How do I make a classic margherita pizza?',2)
        self.assertEqual([x['title'] for x in rows],['Pizza Express Margherita'])
        self.assertLessEqual(len(seen),5)

    def test_taste_question_uses_named_dish(self):
        seen=[]
        def get(url):
            seen.append(url)
            return {'meals':[{'idMeal':'1','strMeal':'Thai Green Curry','strInstructions':'Simmer.'}]}
        with patch.object(r,'_get',side_effect=get):
            r.mealdb('What does a Thai green curry taste like, and what is in it?',2)
        self.assertIn('s=Thai+green+curry',seen[0])

    def test_dietary_constraint_not_dropped_by_token_fallback(self):
        def get(url):
            return {'meals':[{'idMeal':'1','strMeal':'Chickpea Chicken','strInstructions':'Cook chicken.'}]} if 's=chickpeas' in url else {'meals':[]}
        with patch.object(r,'_get',side_effect=get):
            self.assertEqual(r.mealdb('Give me a vegetarian dinner idea with chickpeas',2),[])

    def test_constraint_after_taste_not_trimmed(self):
        seen=[]
        with patch.object(r,'_get',side_effect=lambda u: seen.append(u) or {'meals':[]}):
            r.mealdb('Thai green curry taste like without nuts',2)
        self.assertIn('without+nuts',seen[0])

    def test_filter_before_limit_does_not_hide_later_name_match(self):
        def get(url):
            return {'meals':[{'idMeal':'2','strMeal':'Margherita cocktail','strInstructions':'Mix.'}, {'idMeal':'1','strMeal':'Pizza Express Margherita','strInstructions':'Bake.'}]} if url.endswith('s=margherita') else {'meals':[]}
        with patch.object(r,'_get',side_effect=get):
            self.assertEqual([x['title'] for x in r.mealdb('margherita pizza',1)],['Pizza Express Margherita'])

    def test_single_name_query_unchanged(self):
        seen=[]
        with patch.object(r,'_get',side_effect=lambda u: seen.append(u) or {'meals':[]}):
            self.assertEqual(r.mealdb('margherita',2),[])
        self.assertEqual(len(seen),2)
        self.assertTrue(seen[0].endswith('s=margherita'))

    def test_returned_measure_not_silently_rewritten(self):
        text=r._meal_text({'strIngredient1':'Oregano','strMeasure1':'Peeled and Sliced','strInstructions':'Season.'})
        self.assertIn('Peeled and Sliced Oregano',text)

    def test_failed_api_is_not_recast_as_success(self):
        with patch.object(r,'_get',side_effect=ValueError('Food API HTTP 429; try again shortly.')):
            with self.assertRaisesRegex(ValueError,'429'):
                r.mealdb('classic margherita pizza',2)

    def test_nutrition_comparison_searches_both_foods(self):
        seen=[]
        def get(url):
            seen.append(url)
            name='Feta' if 'search_terms=feta' in url else 'Cheddar'
            return {'products':[{'product_name':name,'url':'https://example.invalid/'+name,'nutriments':{'fat_100g':20}}]}
        with patch.object(r,'_get',side_effect=get):
            rows=r.offfoods('How does the nutrition of feta compare to cheddar?',4)
        self.assertEqual(len(seen),2)
        self.assertIn('search_terms=feta',seen[0])
        self.assertIn('search_terms=cheddar',seen[1])
        self.assertEqual(len(rows),2)
        self.assertIn('Requested comparison food: feta',rows[0]['text'])
        self.assertIn('Packaged-food data point',rows[0]['text'])

    def test_nutrition_comparison_keeps_food_constraints(self):
        seen=[]
        with patch.object(r,'_get',side_effect=lambda u: seen.append(u) or {'products':[]}):
            r.offfoods('How does the nutrition of low sodium feta compare to reduced fat cheddar?',4)
        self.assertIn('search_terms=low+sodium+feta',seen[0])
        self.assertIn('search_terms=reduced+fat+cheddar',seen[1])

    def test_generic_nutrition_question_is_not_split(self):
        seen=[]
        with patch.object(r,'_get',side_effect=lambda u: seen.append(u) or {'products':[]}):
            r.offfoods('Compare feta without nuts to cheddar',4)
        self.assertEqual(len(seen),1)
        self.assertIn('without+nuts',seen[0])

    def test_comparison_limit_one_does_not_return_one_sided_data(self):
        with patch.object(r,'_get') as get:
            self.assertEqual(r.offfoods('How does the nutrition of feta compare to cheddar?',1),[])
            get.assert_not_called()

    def test_comparison_failure_not_hidden_as_complete(self):
        with patch.object(r,'_get',side_effect=[{'products':[{'product_name':'Feta','nutriments':{'fat_100g':20}}]}, ValueError('Food API HTTP 503; try again shortly.')]):
            with self.assertRaisesRegex(ValueError,'503'):
                r.offfoods('How does the nutrition of feta compare to cheddar?',4)

    def test_comparison_empty_side_is_not_presented_as_complete(self):
        with patch.object(r,'_get',side_effect=[{'products':[{'product_name':'Feta','nutriments':{'fat_100g':20}}]}, {'products':[]}]):
            self.assertEqual(r.offfoods('How does the nutrition of feta compare to cheddar?',4),[])

    def test_comparison_labels_products_not_generic_cheese_values(self):
        with patch.object(r,'_get',return_value={'products':[{'product_name':'Cheese product','nutriments':{'fat_100g':20}}]}):
            rows=r.offfoods('How does the nutrition of feta compare to cheddar?',4)
        self.assertTrue(all('Product-specific example, not a typical value for this food.' in row['text'] for row in rows))

    def test_exact_displayed_comparison_example_removes_only_trailing_emoji(self):
        seen=[]
        with patch.object(r,'_get',side_effect=lambda u: seen.append(u) or {'products':[]}):
            r.offfoods('How does the nutrition of feta compare to cheddar? 🧀',6)
        self.assertEqual(len(seen),2)
        self.assertIn('search_terms=feta&',seen[0]);self.assertIn('search_terms=cheddar&',seen[1])

    def test_configured_retrieval_keeps_exact_comparison_and_both_foods(self):
        import sys,urllib.parse
        from chatify import schema
        from chatify.pipeline import Engine
        from chatify.store import Store
        root=Path(__file__).resolve().parents[1]
        cfg=schema.load(str(root/'apps/recipechat/app.yaml'));cfg['provider']={'type':'mock','model':'offline'}
        cfg['retrieval']['query_expansion']=False
        store=Store(':memory:');engine=Engine(cfg,store)
        module=sys.modules['recipe_sources'];seen=[]
        def get(url):
            q=urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('search_terms',[''])[0];seen.append(q)
            if q in ('feta','cheddar'):
                return {'products':[{'product_name':q+' product','url':'https://example.invalid/'+q,'nutriments':{'fat_100g':20}}]}
            return {'products':[]}
        with patch.object(module,'_get',side_effect=get):rows,errors=engine.retrieve(cfg['app']['examples'][2],source_ids=['nutrition'])
        self.assertEqual(seen,['feta','cheddar']);self.assertEqual(errors,{})
        self.assertEqual({x['title'] for x in rows},{'feta product','cheddar product'})

    def test_invalid_crowdsourced_nutrition_not_comparison_evidence(self):
        invalid=[{'fat_100g':8,'saturated-fat_100g':10},{'carbohydrates_100g':1,'sugars_100g':4},{'proteins_100g':101},{'salt_100g':-1},{'fat_100g':float('nan')},{'fat_100g':True}]
        for nutrients in invalid:
            with self.subTest(nutrients=nutrients),patch.object(r,'_get',return_value={'products':[{'product_name':'Invalid product','brands':'Brand','nutriments':nutrients}]}):
                self.assertEqual(r.offfoods('feta',3),[])

    def test_zero_and_component_equal_total_remain_valid(self):
        product={'product_name':'Valid zero','url':'https://example.invalid/zero','nutriments':{'fat_100g':0,'saturated-fat_100g':0,'carbohydrates_100g':3,'sugars_100g':3,'salt_100g':0}}
        with patch.object(r,'_get',return_value={'products':[product]}):rows=r.offfoods('feta',3)
        self.assertEqual(rows[0]['url'],product['url']);self.assertIn('Fat 0g',rows[0]['text']);self.assertIn('Salt 0g',rows[0]['text'])

    def test_brand_only_product_does_not_fill_nutrition_comparison(self):
        with patch.object(r,'_get',return_value={'products':[{'product_name':'Cheese','brands':'Brand'}]}):
            self.assertEqual(r.offfoods('How does the nutrition of feta compare to cheddar?',6),[])

    def test_invalid_first_product_does_not_hide_valid_product_within_page(self):
        products=[{'product_name':'Invalid','nutriments':{'fat_100g':8,'saturated-fat_100g':10}},{'product_name':'Valid','nutriments':{'fat_100g':20}}]
        with patch.object(r,'_get',return_value={'products':products}):rows=r.offfoods('feta',2)
        self.assertEqual([row['title'] for row in rows],['Valid'])

    def test_configured_retrieval_does_not_rescue_missing_comparison_side_with_broader_query(self):
        import sys,urllib.parse
        from chatify import schema
        from chatify.pipeline import Engine
        from chatify.store import Store
        cfg=schema.load(str(Path(__file__).resolve().parents[1]/'apps/recipechat/app.yaml'))
        cfg['provider']={'type':'mock','model':'offline'};cfg['retrieval']['query_expansion']=False
        engine=Engine(cfg,Store(':memory:'));seen=[]
        def get(url):
            q=urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('search_terms',[''])[0];seen.append(q)
            if q=='cheddar':return {'products':[]}
            return {'products':[{'product_name':'Feta','url':'https://example.invalid/feta','nutriments':{'fat_100g':20}}]}
        with patch.object(sys.modules['recipe_sources'],'_get',side_effect=get):rows,errors=engine.retrieve(cfg['app']['examples'][2],source_ids=['nutrition'])
        self.assertEqual(rows,[]);self.assertEqual(errors,{});self.assertEqual(seen,['feta','cheddar'])

    def test_other_sources_keep_generic_query_ladder(self):
        from chatify import schema
        from chatify.pipeline import Engine
        from chatify.store import Store
        from types import SimpleNamespace
        cfg=schema.validate({'provider':{'type':'mock'},'sources':[{'id':'public','type':'wikipedia'}]})
        engine=Engine(cfg,Store(':memory:'));seen=[]
        engine.connectors={'public':SimpleNamespace(search=lambda q,k: seen.append(q) or [])}
        question='How does the nutrition of feta compare to cheddar?'
        engine.retrieve(question,source_ids=['public'])
        self.assertEqual(seen,engine.queries(question));self.assertGreater(len(seen),1)
