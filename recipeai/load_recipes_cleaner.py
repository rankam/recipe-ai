import json
import string 
from recipeai.recipes.ingredient_classifier import predict
from recipeai.recipes.models import * 
import logging

KNOWN_UNITS = [
        "teaspoon",
        "tsp",
        "tablespoon",
        "tbsp",
        "tbs",
        "ounes",
        "fluid ounce",
        "fl oz",
        "oz",
        "ounce",
        "ounces",
        "cup",
        "c",
        "pint",
        "pt",
        "quart",
        "qt",
        "gallon",
        "gal",
        "milliliter",
        "ml",
        "liter",
        "litre",
        "l",
        "L",
        "pound",
        "lb",
        "mg",
        "milligram",
        "gram",
        "kg",
        "kilogram",
        "small",
        "large",
        "medium"
] 

def read_recipes(short=True):
    if short:
        recipes_filepath = '/Users/aaronrank/Downloads/recipe1M_layers/layer1_100.json'
    else:
        recipes_filepath = '/Users/aaronrank/Downloads/recipe1M_layers/layer1.json'
    with open(recipes_filepath, 'r') as f:
        recipes = json.loads(f.read())
    return recipes

def is_fraction(val):
    if '/' in val:
        val_arr = val.split('/')
        if len(val_arr) == 2:
            try:
                float(val_arr[0]) / float(val_arr[1])
                return True
            except:
                return False
    return False

user_id = 'cdc1c86e-068a-45a0-95b8-22fdf54744c6'

user = User.objects.get(id=user_id)

{'ingredients': [{'text': '1 c. elbow macaroni'},
  {'text': '1 c. cubed American cheese (4 ounce.)'},
  {'text': '1/2 c. sliced celery'},
  {'text': '1/2 c. minced green pepper'},
  {'text': '3 tbsp. minced pimento'},
  {'text': '1/2 c. mayonnaise or possibly salad dressing'},
  {'text': '1 tbsp. vinegar'},
  {'text': '3/4 teaspoon salt'},
  {'text': '1/2 teaspoon dry dill weed'}],
 'url': 'http://cookeatshare.com/recipes/dilly-macaroni-salad-49166',
 'partition': 'train',
 'title': 'Dilly Macaroni Salad Recipe',
 'id': '000033e39b',
 'instructions': [{'text': 'Cook macaroni according to package directions; drain well.'},
  {'text': 'Cold.'},
  {'text': 'Combine macaroni, cheese cubes, celery, green pepper and pimento.'},
  {'text': 'Blend together mayonnaise or possibly salad dressing, vinegar, salt and dill weed; add in to macaroni mix.'},
  {'text': 'Toss lightly.'},
  {'text': 'Cover and refrigeratewell.'},
  {'text': 'Serve salad in lettuce lined bowl if you like.'},
  {'text': 'Makes 6 servings.'}]}




def parse_recipes(recipes):
    ci_cache = {}
    while recipes:
        recipe = recipes[0]
        try:
            name = recipe['title']
            ingredients = []
            common_ingredients = []
            for ingredient in recipe['ingredients']:
                ingredient_text = ingredient.get('text')
                ingredient_name, unit, unit_value = parse_ingredient_text(ingredient_text)
                if len(ingredient_name) > 160:
                    continue
                common_ingredient, confidence = predict(ingredient_name)
                common_ingredient_obj = ci_cache.get(common_ingredient, None)
                if common_ingredient_obj is None:
                    common_ingredient_obj = CommonIngredient.objects.get(label=common_ingredient)
                    ci_cache[common_ingredient] = common_ingredient_obj
                val = {'unit_type': unit, 'units': unit_value, 'name': ingredient_name,
                'confidence': confidence, 'common_ingredient': common_ingredient_obj, 'user': user}
                ing = Ingredient(**val)
                ing.save()
                ingredients.append(ing)
                common_ingredients.append(common_ingredient_obj)
            _recipe = {'name': name, 'user': user}
            rec_obj = Recipe(**_recipe)
            rec_obj.save()
            rec_obj.ingredients.set(ingredients)
            rec_obj.common_ingredients.set(common_ingredients)
        except Exception as e:
            print(f'Error {e}')  
        if len(recipes) % 100 == 0:
            print(len(recipes), 'left')
        recipes.pop(0) 


def parse_ingredient_text(text):
    unit = ''
    unit_value = ''
    ingredient_name = ''
    text = text.lower().strip()
    for token in text.split():
        if is_fraction(token):
            try:
                token = str(round(eval(token), 2))
            except Exception as e:
                print('Error evaluating fraction', token, 'Error -', e)
            unit_value += f'{token} '
        else:
            for p in string.punctuation:
                if p == '-':
                    token = token.replace(p, ' ')
                else:
                    token = token.replace(p, '')
            if token.isnumeric() or token.isdecimal():
                unit_value += f'{token} '
            elif token in KNOWN_UNITS or f'{token}s' in KNOWN_UNITS or token.rstrip('s') in KNOWN_UNITS:
                unit = token 
            else: 
                ingredient_name += f'{token} '
    return ingredient_name.strip(),unit.strip(),unit_value.strip()


dupes = [
'Naan Bread',
'Chicken Cacciatore',
'Black Bean Hummus',
'White Chili',
'Wild Rice Salad',
'Baked Ziti',
'Vegetable Cheese Soup',
'Meatloaf',
'Mustard Potato Salad',
'Black-eyed Pea Salad',
'Baked Potato Soup',
'Irresistible Peanut Butter Cookies',
'Spaghetti Pie',
'Creamy Baked Ziti',
'Zucchini Cakes',
'Banana Bread',
'CERTO Pepper Relish and Jelly',
'Zucchini Bread',
'Sourdough Starter',
'Chicken Enchiladas',
'Pumpkin Flan',
'Meatballs',
'Mango Lassi',
'London Fog',
'Espresso Martini',
'Chicken Noodle Soup',
'Stuffed peppers',
'Crispy Fried Chicken',
'Ultimate Lasagna Bolognese _ Tyler Florence',
'Red Wine Vinaigrette']


for name in dupes:
    recipes = list(Recipe.objects.filter(name=name))
    while len(recipes) > 1:
        recipe = recipes[0]
        recipe.delete()
        recipes.pop(0)




