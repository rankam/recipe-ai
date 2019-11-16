from django.db import connection
AVAILABLE_RECIPES_QUERY = """
with recipe_user_common_ingredients as (
    select
        r.id,
        r.name, 
        rci.recipe_id,
        rci.commoningredient_id,
        json_build_object(
            'ingredient',json_build_object(
                'id', i.id,
                'created_at', i.created_at,
                'name', i.name,
                'units', i.units,
                'unit_type', i.unit_type,
                'confidence', i.confidence,
                'common_ingredient_id', i.common_ingredient_id,
                'user_id', i.user_id,
                'user_common_ingredient', row_to_json(uci)
            )
        ) as ingredients,
        uci.is_available
    from recipes_recipe_common_ingredients rci 
    join recipes_usercommoningredient uci on rci.commoningredient_id = uci.common_ingredient_id 
    join recipes_recipe_ingredients ri on rci.recipe_id = ri.recipe_id 
    join recipes_ingredient i on ri.ingredient_id = i.id and i.common_ingredient_id = rci.commoningredient_id 
    join recipes_recipe r on r.id = rci.recipe_id
    where uci.user_id = %s
),
recipe_ingredient_count as (
    select 
        recipe_id, 
        count(ruci.commoningredient_id) as num_ings
    from recipe_user_common_ingredients ruci 
    group by recipe_id 
),
recipe_available_ingredient_count as (
    select 
        recipe_id, 
        count(ruci.commoningredient_id) as num_ings
    from recipe_user_common_ingredients ruci 
    where is_available = true
    group by recipe_id 
),
available_recipes as (
    select r.recipe_id 
    from recipe_ingredient_count r join recipe_available_ingredient_count ai using(recipe_id) 
    where (r.num_ings - ai.num_ings) < %s and r.num_ings > 3
)
select 
    row_to_json(recipes) 
from (
    select 
        r.id,
        r.name, 
        array_agg(ingredients) as ingredients
    from recipe_user_common_ingredients r 
    join available_recipes ar on r.recipe_id = ar.recipe_id 
    group by r.name,r.id
    ) as recipes
"""

RECIPES_BY_USER_COMMON_INGREDIENT_QUERY = """  
    select 
        row_to_json(recipes)
    from (select
                r.id,
                r.name,
                r.created_at,
                r.user_id,
                array_agg(row_to_json(i)) as ingredients,
                array_agg(row_to_json(uci)) as user_common_ingredient
            from recipes_recipe_common_ingredients rci 
            join recipes_usercommoningredient uci on rci.commoningredient_id = uci.common_ingredient_id 
            join recipes_recipe_ingredients ri on rci.recipe_id = ri.recipe_id 
            join recipes_ingredient i on ri.ingredient_id = i.id and i.common_ingredient_id = rci.commoningredient_id 
            join recipes_recipe r on r.id = rci.recipe_id
            where uci.user_id = %s 
            group by 
                r.id,
                r.name,
                r.created_at,
                r.user_id
        ) as recipes
"""    

def query(q):
    with connection.cursor() as cursor:
        cursor.execute(q)
        results = cursor.fetchall()
    return [res[0] for res in results] if results else []

def fetch_recipes_by_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute(RECIPES_BY_USER_COMMON_INGREDIENT_QUERY, [user_id])
        results = cursor.fetchall()
    return [res[0] for res in results] if results else []

def fetch_available_recipes(user_id, num_missing_ings=2):
    with connection.cursor() as cursor:
        cursor.execute(AVAILABLE_RECIPES_QUERY, [user_id, num_missing_ings])
        results = cursor.fetchall()
    return [res[0] for res in results] if results else []
