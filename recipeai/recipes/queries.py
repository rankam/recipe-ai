from django.db import connection
AVAILABLE_RECIPES_QUERY = '''
with ings as (
	select distinct 
		id, 
		common_ingredient, 
		is_available ,
		name,
                confidence
	from recipes_ingredient
        where user_id = %s
),
recipes as (
	select 
		common_ingredient,
		recipe_id,
		rr.name,
		is_available,
		i.name as ingredient
	from recipes_recipe_ingredients r 
	join recipes_recipe rr on r.recipe_id = rr.id 
	join ings i on r.ingredient_id = i.id 
),

avail as (

	select array_agg(common_ingredient) as common_ings, array_agg(name) as my_ings from ings where is_available = true
        and confidence > .98
),

full_recipes as (
	select recipe_id, 
        array_agg(common_ingredient) as common_ings, 
        array_agg(ingredient) as ingredients 
        from recipes group by recipe_id
)
select recipe_id from full_recipes 
where (select common_ings from avail) @> common_ings
'''



def fetch_available_recipes(user_id):
    with connection.cursor() as cursor:
        cursor.execute(AVAILABLE_RECIPES_QUERY, [user_id])
        results = cursor.fetchall()
    return [res[0] for res in results] if results else []
