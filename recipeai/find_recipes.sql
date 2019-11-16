with recipe_user_common_ingredients as (

    select
        r.name, 
        rci.recipe_id,
        rci.commoningredient_id,
        i.name as ingredient,
        uci.is_available
    from recipes_recipe_common_ingredients rci 
    join recipes_usercommoningredient uci on rci.commoningredient_id = uci.common_ingredient_id 
    join recipes_recipe_ingredients ri on rci.recipe_id = ri.recipe_id 
    join recipes_ingredient i on ri.ingredient_id = i.id and i.common_ingredient_id = rci.commoningredient_id 
    join recipes_recipe r on r.id = rci.recipe_id
    where uci.user_id = 'cdc1c86e-068a-45a0-95b8-22fdf54744c6'
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
    where (r.num_ings - ai.num_ings) < 2 and r.num_ings > 3
)
select 
    r.name, 
    array_agg(
        json_build_object(
            'common_ingredient', commoningredient_id, 
            'is_available', is_available, 
            'ingredient', ingredient
            )
        ) as common_ingredients
from recipe_user_common_ingredients r 
join available_recipes ar on r.recipe_id = ar.recipe_id 
group by r.name;

