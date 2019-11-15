import json


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

from recipeai.recipes.models import CommonIngredient 
from recipeai.recipes.models import Ingredient 
from recipeai.users.models import User
from recipeai.recipes.models import Recipe
import fasttext
training_filepath = '/Users/aaronrank/Developer/ingredient-classifier/custom.vocab.train'
# training =[]
# with open(training_filepath, 'r') as f:
#   for line in f.readlines():
#       vals = line.split()
#       _id = vals[0]
#       text = ' '.join(vals[1:])
#       data = {'label': _id, 'name': text}
#       training.append(data)
#       ci = CommonIngredient(**data)
#       ci.save()
model = fasttext.train_supervised(
    input=training_filepath, 
    lr=.75, 
    epoch=100, 
    wordNgrams=2, 
    bucket=100000, 
    dim=10, 
    neg=10,
    loss='hs',
    ws=5
 )
import string
recipes_filepath = '/Users/aaronrank/Downloads/recipe1M_layers/layer1.json'
user_id = 'cdc1c86e-068a-45a0-95b8-22fdf54744c6'
user = User.objects.get(id=user_id)
c = 0
with open(recipes_filepath, 'r') as f:
    print('reading file')
    recipes = json.loads(f.read())
    print('file read')
    c = 0
    for r in recipes:
        c += 1
        if c > 100: 
            break
        name = r['title']
        ingredients = []
        # cis = []
        for ingredient in r['ingredients']:
            unit = ''
            unit_value = ''
            ingredient_name = ''
            ingredient_text = ingredient['text'].lower()
            for p in string.punctuation:
                ingredient_text = ingredient_text.replace(p, '')
            ingredient_text = ingredient_text.strip()
            for token in ingredient_text.split():
                if token.isnumeric() or is_fraction(token) or token.isdecimal():
                    unit_value += f'{token} '
                elif token in KNOWN_UNITS or f'{token}s' in KNOWN_UNITS or token.rstrip('s') in KNOWN_UNITS:
                    unit = token 
                else: 
                    ingredient_name += f'{token} '
            unit_value = unit_value.strip()
            ingredient_name = ingredient_name.strip() 
            clf = model.predict(ingredient_name)
            common_ingredient = clf[0][0]
            confidence = clf[1][0]
            val = {'unit_type': unit, 'units': unit_value, 'name': ingredient_name,
            'confidence': confidence, 'common_ingredient': common_ingredient, 'user': user}
            ing = Ingredient(**val)
            ing.save()
            ingredients.append(ing)
            # ci = CommonIngredient({'name': common_ingredient, 'label': common_ingredient, 'uuid': '123'})
            # ci.save()
            # cis.append(ci)
        recipe = {'name': name, 'user': user}
        rec_obj = Recipe(**recipe)
        rec_obj.save()
        rec_obj.ingredients.set(ingredients)
        print(f'Recipe {rec_obj.name} ({rec_obj.id}) saved!')

my_ings = set()
import random
for i in Ingredient.objects.all():
    if i.common_ingredient not in my_ings and random.random() <= .2 and len(my_ings) < 23:
        my_ings.add(i)

