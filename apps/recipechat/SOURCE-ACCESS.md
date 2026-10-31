# Recipe source access qualification, 31 October 2026

TheMealDB is not an unrestricted keyless production source. Its current documentation distinguishes development/educational key `1` from production/supporter access:
- https://themealdb.com/documentation
- https://www.themealdb.com/api.php
- https://www.themealdb.com/docs_api_guide.php

Set `THEMEALDB_API_KEY` to an already-authorized production key. No purchase or subscription was made. Educational local testing can explicitly set `CHATIFY_MEALDB_EDUCATIONAL_DEMO=1`; this is not a production entitlement. Without either, the recipe connector reports unavailable while other sources can continue. No production key was found in the available saved credential metadata during this check. A saved USDA FoodData Central key is a separate source, not a recipe-access entitlement.

Open Food Facts current documentation sets search at 10 requests/minute/IP and product reads at 15/minute/IP, warning of IP bans:
https://openfoodfacts.github.io/openfoodfacts-server/api/

The local connector now spaces search calls by at least 6.1 seconds and caches identical requests for 10 minutes with a 64-entry bound. This is per-process protection, not coordination across multiple processes or hosts sharing an IP. A shared deployment needs centralized pacing or separate source routing before claiming compliance at scale. No live deployment was changed.

Four source-access/cache contracts pass. No actual production RecipeChat answer has been qualified under a production TheMealDB key. The source warning remains a ship blocker for recipe results, not a reason to purchase access automatically.
