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
