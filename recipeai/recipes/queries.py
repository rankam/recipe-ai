from django.db import connection

AVAILABLE_RECIPES_QUERY = '''
with recipe_ingredient_count as (
    select 
        recipe_id, 
        count(*) as num_ingredients 
    from recipes_recipe_ingredients 
    group by 1
),

user_recipe_ingredient_count as (
    select 
        recipe_id,
        count(*) as num_ingredients
    from 
        recipes_usercommoningredient uci 
        join recipes_recipe_common_ingredients rci on uci.common_ingredient_id = rci.commoningredient_id
    where 
        uci.user_id = %s
    group by 1
)
select row_to_json(recipes) from (
select 
    recipe_id as id,
    name, 
    num_missing_ingredients,
    sum(calories) as calories,
    sum(protein) as protein,
    array_agg(ingredient::jsonb ||
        jsonb_build_object(
            'nutrients', nutrient_details.nutrients
        ) || jsonb_build_object('nuts',nuts)
    ) as ingredients    
    from 
(
select 
    distinct
    r.id as recipe_id,
    r.name,
    (coalesce(ric.num_ingredients,0) - coalesce(uric.num_ingredients,0)) as num_missing_ingredients,
    i.common_ingredient_id,
    jsonb_build_object(
        'id', i.id,
        'created_at', i.created_at,
        'name', i.name,
        'display_name', ci.display_name,
        'units', i.units,
        'unit_type', i.unit_type,
        'confidence', i.confidence,
        'common_ingredient_id', i.common_ingredient_id,
        'user_id', i.user_id,
        'is_available', (uci.user_id is not null)::text,
        'user_common_ingredient', jsonb_build_object(
            'id', uci.id,
            'user_id', uci.user_id,
            'common_ingredient_id', uci.common_ingredient_id
        ),        
        'common_ingredient', jsonb_build_object(
            'display_name', ci.display_name,
            'nutrients', array_agg(jsonb_build_object(
                    'id', n.id,
                    'amount', cin.amount,
                    'name', n.name,
                    'unit_type', n.unit_type
                )
            )
        )        
    ) as ingredient
from recipe_ingredient_count ric join user_recipe_ingredient_count uric using(recipe_id)
join recipes_recipe r on ric.recipe_id = r.id
left join recipes_recipe_ingredients rri on ric.recipe_id = rri.recipe_id 
left join recipes_ingredient i on rri.ingredient_id = i.id 
left join recipes_commoningredient ci on i.common_ingredient_id = ci.label
left join (select * from recipes_usercommoningredient where user_id = %s) uci on i.common_ingredient_id = uci.common_ingredient_id
left join recipes_common_ingredient_nutrient cin on ci.label = cin.common_ingredient_id 
left join recipes_nutrient n on cin.nutrient_id = n.id
where 
    ric.num_ingredients > 3 and 
    ((coalesce(ric.num_ingredients,0) - coalesce(uric.num_ingredients,0)) <= %s or uric.num_ingredients is null)
group by 
    r.id,r.name,i.common_ingredient_id,i.id,i.created_at,i.name,ci.display_name, (coalesce(ric.num_ingredients,0) - coalesce(uric.num_ingredients,0)), i.units, i.unit_type, i.confidence, i.common_ingredient_id, i.user_id, (uci.user_id is not null), uci.id, uci.user_id, uci.common_ingredient_id
) as available_recipes 
left join (
    select
        ci.label as common_ingredient_id,
        sum(case when n.name = 'Energy' then cin.amount::numeric else 0 end) as  calories,
        sum(case when n.name = 'Protein' then cin.amount::numeric else 0 end) as  protein,
        jsonb_build_object(
            'calories', sum(case when n.name = 'Energy' then cin.amount::numeric else 0 end),
            'protein', sum(case when n.name = 'Protein' then cin.amount::numeric else 0 end)
        ) nuts,
        array_agg(
            json_build_object(
                'name', n.name,
                'unit_type',n.unit_type,
                'amount', cin.amount,
                'common_ingredient_id',ci.label
            )
        ) nutrients
    from recipes_commoningredient ci 
    left join recipes_common_ingredient_nutrient cin on ci.label =
    cin.common_ingredient_id 
    left join recipes_nutrient n on cin.nutrient_id = n.id
    group by ci.label, ci.display_name
) as nutrient_details  on available_recipes.common_ingredient_id = nutrient_details.common_ingredient_id
group by 1,2,3
) as recipes
'''


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

FETCH_RECIPE_BY_ID_QUERY = """
select row_to_json(recipes) from (
select 
    recipe_id as id,
    name, 
    sum(coalesce(calories, 0)) as calories,
    sum(coalesce(protein, 0)) as protein,
    array_agg(ingredient::jsonb ||
        jsonb_build_object(
            'nutrients', nutrient_details.nutrients
        ) || jsonb_build_object('nuts',nuts)
    ) as ingredients    
    from 
(
select 
    distinct
    r.id as recipe_id,
    r.name,
    i.common_ingredient_id,
    jsonb_build_object(
        'id', i.id,
        'created_at', i.created_at,
        'name', i.name,
        'display_name', ci.display_name,
        'units', i.units,
        'unit_type', i.unit_type,
        'confidence', i.confidence,
        'common_ingredient_id', i.common_ingredient_id,
        'user_id', i.user_id,
        'is_available', (uci.user_id is not null)::text,
        'user_common_ingredient', jsonb_build_object(
            'id', uci.id,
            'user_id', uci.user_id,
            'common_ingredient_id', uci.common_ingredient_id
        ),
        'common_ingredient', jsonb_build_object(
            'display_name', ci.display_name,
            'nutrients', array_agg(jsonb_build_object(
                    'id', n.id,
                    'amount', cin.amount,
                    'name', n.name,
                    'unit_type', n.unit_type
                )
            )
        )
    ) as ingredient
from recipes_recipe r 
left join recipes_recipe_ingredients rri on r.id = rri.recipe_id 
left join recipes_ingredient i on rri.ingredient_id = i.id 
left join recipes_commoningredient ci on i.common_ingredient_id = ci.label
left join (select * from recipes_usercommoningredient where user_id = %s) uci on i.common_ingredient_id = uci.common_ingredient_id
left join recipes_common_ingredient_nutrient cin on ci.label = cin.common_ingredient_id 
left join recipes_nutrient n on cin.nutrient_id = n.id
where 
    r.id = %s
group by 
    r.id,r.name,i.common_ingredient_id,i.id,i.created_at,i.name,ci.display_name, i.units, i.unit_type, i.confidence, i.common_ingredient_id, i.user_id, (uci.user_id is not null), uci.id, uci.user_id, uci.common_ingredient_id
) as available_recipes 
left join (
    select
        ci.label as common_ingredient_id,
        sum(case when n.name = 'Energy' then cin.amount::numeric else 0 end) as  calories,
        sum(case when n.name = 'Protein' then cin.amount::numeric else 0 end) as  protein,
        jsonb_build_object(
            'calories', sum(case when n.name = 'Energy' then cin.amount::numeric else 0 end),
            'protein', sum(case when n.name = 'Protein' then cin.amount::numeric else 0 end)
        ) nuts,
        array_agg(
            json_build_object(
                'name', n.name,
                'unit_type',n.unit_type,
                'amount', cin.amount,
                'common_ingredient_id',ci.label
            )
        ) nutrients
    from recipes_commoningredient ci 
    left join recipes_common_ingredient_nutrient cin on ci.label =
    cin.common_ingredient_id 
    left join recipes_nutrient n on cin.nutrient_id = n.id
    group by ci.label, ci.display_name
) as nutrient_details  on available_recipes.common_ingredient_id = nutrient_details.common_ingredient_id
group by 1,2
) as recipes
"""

SEARCH_ALL_COMMON_INGREDIENTS_QUERY = """

    select 
        label,
        display_name,
        created_at
    from recipes_commoningredient 
    where 
        case 
            when %s = 'empty' then 1 = 1 
            else to_tsvector(display_name) @@ to_tsquery(%s) is true
        end

"""

SEARCH_USER_COMMON_INGREDIENTS_QUERY = """

    select 
        id,
        user_id as user,
        display_name,
        common_ingredient_id as common_ingredient
    from recipes_usercommoningredient uci join recipes_commoningredient ci on uci.common_ingredient_id = ci.label
    where 
        user_id = %s and
        case 
            when %s = 'empty' then 1 = 1 
            else to_tsvector(display_name) @@ to_tsquery(%s) is true
        end      
    order by uci.id desc  

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

def fetch_available_recipes(user_id, confidence_level=0, num_missing_ings=0, search_term='empty'):
    if search_term is None:
        search_term = 'empty'   
    elif search_term == '':
        search_term = 'empty'         
    elif search_term != 'empty':
        search_term += ':*'

    with connection.cursor() as cursor:
        cursor.execute(AVAILABLE_RECIPES_QUERY,
                [
                    user_id,
                    user_id,
                    # search_term,
                    # search_term,
                    # confidence_level,
                    num_missing_ings
                ])
        results = cursor.fetchall()
    # return results
    return [res[0] for res in results] if results else []

def search_common_ingredients(search_term):
    if search_term is None:
        search_term = 'empty'   
    elif search_term == '':
        search_term = 'empty'         
    elif search_term != 'empty':
        search_term += ':*'        
    with connection.cursor() as cursor:
        cursor.execute(SEARCH_ALL_COMMON_INGREDIENTS_QUERY,
                [
                    search_term,
                    search_term
                ])
        results = cursor.fetchall()
    return [{'label':res[0], 'display_name': res[1], 'created_at': res[2]} for res in results] if results else []    

def search_user_common_ingredients(user_id, search_term):
    if search_term is None:
        search_term = 'empty'   
    elif search_term == '':
        search_term = 'empty'         
    elif search_term != 'empty':
        search_term += ':*'    
    with connection.cursor() as cursor:
        cursor.execute(SEARCH_USER_COMMON_INGREDIENTS_QUERY,
                [
                    user_id,
                    search_term,
                    search_term
                ])
        results = cursor.fetchall()
    return [{'id':res[0], 'user': res[1], 'display_name': res[2], 'common_ingredient': res[3]} for res in results] if results else []    

def fetch_recipe_by_id(user_id, recipe_id):    
    with connection.cursor() as cursor:
        cursor.execute(FETCH_RECIPE_BY_ID_QUERY,
                [
                    user_id,
                    recipe_id
                ])
        results = cursor.fetchall()
    return [res[0] for res in results] if results else []    



