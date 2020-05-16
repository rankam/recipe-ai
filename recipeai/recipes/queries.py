from django.db import connection
AVAILABLE_RECIPES_QUERY = """

with recipe_user_common_ingredients as (
    select 
        r.id,
        r.name, 
        rci.recipe_id,
        rci.commoningredient_id,
        i.confidence,
        json_build_object(
            'id', i.id,
            'created_at', i.created_at,
            'name', i.name,
            'units', i.units,
            'unit_type', i.unit_type,
            'confidence', i.confidence,
            'common_ingredient_id', i.common_ingredient_id,
            'user_id', i.user_id,
            'user_common_ingredient', row_to_json(uci)
     --       'nutrients', n.nutrients
        ) as ingredient
    from recipes_recipe r 
    join recipes_recipe_common_ingredients rci on r.id = rci.recipe_id
    join recipes_recipe_ingredients ri on rci.recipe_id = ri.recipe_id 
    join recipes_usercommoningredient uci on rci.commoningredient_id = uci.common_ingredient_id 
    
    join recipes_ingredient i on ri.ingredient_id = i.id and i.common_ingredient_id = rci.commoningredient_id 
    --left recipes_recipe r on r.id = rci.recipe_id
    --join nutrients n on uci.common_ingredient_id = n.common_ingredient_id
    where uci.user_id = %s and uci.common_ingredient_id is not null
),
recipe_ingredient_count as (
    select 
        recipe_id, 
        count(ingredient_id) as num_ings
    from recipes_recipe_ingredients ruci 
    group by recipe_id 
),
recipe_available_ingredient_count as (
    select 
        recipe_id, 
        count(ruci.commoningredient_id) as num_ings
    from recipe_user_common_ingredients ruci 
    group by recipe_id 
    having min(confidence) >= %s 
),
available_recipes as (
    select r.recipe_id 
    from recipe_ingredient_count r join recipe_available_ingredient_count ai using(recipe_id) 
    where (r.num_ings - ai.num_ings) <= %s and r.num_ings > 3
)
select 
    row_to_json(recipes) 
from (
    select 
        r.id,
        r.name, 
        array_agg(ingredient) as ingredients
        --array_agg(ingredient::jsonb ||
        --jsonb_build_object('nutrients', n.nutrients)) as ingredients
    from recipe_user_common_ingredients r 
    join available_recipes ar on r.recipe_id = ar.recipe_id 
    -- join (
    --     select 
    --         ci.label as common_ingredient_id,
    --         array_agg(
    --             json_build_object(
    --                 'name', n.name,
    --                 'unit_type',n.unit_type,
    --                 'amount', cin.amount,
    --                 'common_ingredient_id',ci.label
    --                     )
    --                 ) nutrients
    --     from recipes_commoningredient ci 
    --     left join recipes_common_ingredient_nutrient cin on ci.label =
    --     cin.common_ingredient_id 
    --     left join recipes_nutrient n on cin.nutrient_id = n.id
    --     group by ci.label

    -- ) as n on r.ingredient ->> 'common_ingredient_id' = n.common_ingredient_id 
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
                array_agg(
                    json_build_object(
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

def fetch_available_recipes(user_id, confidence_level=0, num_missing_ings=0):
    with connection.cursor() as cursor:
        cursor.execute(AVAILABLE_RECIPES_QUERY,
                [
                    user_id,
                    confidence_level,
                    num_missing_ings
                ])
        results = cursor.fetchall()
    return [res[0] for res in results] if results else []
