with ings as (

	select distinct id, common_ingredient, is_available from recipes_ingredient

),

recipes as (

	select 
		common_ingredient,
		recipe_id,
		rr.name,
		is_available
	from recipes_recipe_ingredients r 
	left join recipes_recipe rr on r.recipe_id = rr.id 
	left join ings i on r.ingredient_id = i.id 


), foo as (
select name 
from recipes
group by name, is_available
having (count(is_available = false or null) < 2 or count(is_available = false or null) is null) 
)

select 
	r.name, 
	array_agg(r.common_ingredient) filter (where is_available = true) as available_ingredients, 
	array_agg(r.common_ingredient) filter (where is_available = false) as unavailable_ingredients
from recipes r 
join foo 
using(name) 
group by r.name 

-- my_ings as (

-- 	select array_agg(common_ingredient) as ings
-- 	from recipes_ingredient where is_available = 'true'
-- )

select r.name from recipes r 


select name as recipe_name 
from recipes r 
where (select ings::varchar[] from my_ings)  @> r.ings::varchar[]

