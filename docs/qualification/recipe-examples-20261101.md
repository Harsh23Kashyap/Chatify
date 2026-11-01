# RecipeChat example qualification, 2026-11-01

Local working-branch candidate only. No deployed gallery acceptance.

The unchanged MealDB adapter returned zero recipes for all three full example questions: classic margherita pizza, Thai green curry taste, and vegetarian chickpeas. Actual current free API responses confirmed shorter named queries found recipes.

Candidate preserves the requested name tokens, removes the example's terminal taste-question wording and optional classic descriptor, and tries at most three additional token-name queries. Returned fallback titles must contain every requested name token. Four deterministic controls cover title-order differences, an unrelated same-token cocktail, dietary constraints, and constraints after a taste phrase.

Actual candidate connector requests return Pizza Express Margherita and Thai Green Curry for the first two full examples. The vegetarian chickpea example still returns none: no dietary constraint was discarded to fabricate a match. This remains an incomplete gallery capability.

Actual configured ranking of the first two examples puts these recipes first, but one separate raw-ranked margherita run also retained an unrelated Royal Enfield Wikipedia page. Ranking improvement is not broad source relevance acceptance.

Two actual full local Engine.ask calls used explicit OpenAI gpt-4.1-mini qualification provider override and query expansion off. The margherita answer preserved the recipe's quantities and 230 C / 10-12 minute oven instructions, but repeated the source's anomalous "Peeled and Sliced Oregano" and asserted the recipe matched traditional Neapolitan pizza despite differences in the second source. Nutrition connector returned a ValueError on that call. Thai curry returned the cited recipe and quantities, but generalized cuisine-wide sweet/sour/salty/spicy characteristics to this dish and added creamy texture from ingredients. Automated ledgers marked these sentences supported. Neither is a clean semantic pass; answer_verified remains false.

Exact publisher pages independently fetched:
- https://www.themealdb.com/meal/53014
- https://www.themealdb.com/meal/52814
- https://en.wikipedia.org/wiki/Pizza_Margherita
- https://en.wikipedia.org/wiki/Thai_cuisine

This candidate repairs demonstrated recipe name retrieval, not source truth, flavor entailment, vegetarian coverage, reliable nutrition, full Build, or hosted selected-route acceptance. No generated helper was run or installed.

20:24 actual-model prompt experiment on the same preserved real passages did not fix semantics. A recipe-specific instruction about source anomalies and cuisine-versus-dish claims was tested in two actual full Engine.ask calls, then removed: it still repeated anomalous oregano advice, added home-oven suitability absent from evidence, and explicitly generalized cuisine flavor to this dish. No ineffective prompt change was retained or promoted. These were bounded diagnostics, not a tuning loop. Eight adapter controls and sixteen existing gallery tests pass; source correction remains retrieval-only.
