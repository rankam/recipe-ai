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

from recipeai.recipes.models import CommonIngredient , UserCommonIngredient
from recipeai.recipes.models import Ingredient 
from recipeai.users.models import User
from recipeai.recipes.models import Recipe
from recipeai.recipes.ingredient_classifier import predict
import fasttext
import json


training_filepath = '/Users/aaronrank/Developer/ingredient-classifier/custom.vocab.train'
# model = fasttext.train_supervised(
#     input=training_filepath, 
#     lr=.75, 
#     epoch=100, 
#     wordNgrams=2, 
#     bucket=100000, 
#     dim=10, 
#     neg=10,
#     loss='hs',
#     ws=5
#  )

user_id = 'cdc1c86e-068a-45a0-95b8-22fdf54744c6'

user = User.objects.get(id=user_id)
foo = set()
with open(training_filepath, 'r') as f:
    for line in f.readlines():
        try:
            vals = line.split()
            _id = vals[0]
            text = ' '.join(vals[1:])
            data = {'label': _id}
            foo.add(_id)
        except Exception as e:
            print(f'Errror {e}')

            foo.add(_id)
import datetime
for _id in foo:            
    try:
        ci = CommonIngredient(**{'label': _id})
        ci.save()
        # ci = CommonIngredient.objects.get(label=_id)
        uci_data = {'user': user, 'common_ingredient': ci}
        uci = UserCommonIngredient(**uci_data)
        uci.save()
    except Exception as e:
        print(f'error {e}')
        continue


import string
recipes_filepath = '/Users/aaronrank/Downloads/recipe1M_layers/layer1.json'
recipes_100_filepath = '/Users/aaronrank/Downloads/recipe1M_layers/layer1_100.json'

# c = 0
with open(recipes_100, 'r') as f:
    print('reading file')
    recipes = json.loads(f.read())
    print('file read')
    # c = 0
    for _idx_, r in enumerate(recipes[:1000]):
        # c += 1
        # if c <= 100:
        #     continue
        # if c > 1000: 
        #     break
        try:
            name = r['title']
            ingredients = []
            common_ingredients = []
            # cis = []
            for ingredient in r['ingredients']:
                unit = ''
                unit_value = ''
                ingredient_name = ''
                ingredient_text = ingredient['text'].lower()
                # for p in string.punctuation:
                #     ingredient_text = ingredient_text.replace(p, '')
                ingredient_text = ingredient_text.strip()
                for token in ingredient_text.split():
                    if is_fraction(token):
                        unit_value += f'{token} '
                    else:
                        for p in string.punctuation:
                            token = token.replace(p, '')
                        if token.isnumeric() or token.isdecimal():
                            unit_value += f'{token} '
                        elif token in KNOWN_UNITS or f'{token}s' in KNOWN_UNITS or token.rstrip('s') in KNOWN_UNITS:
                            unit = token 
                        else: 
                            ingredient_name += f'{token} '
                unit_value = unit_value.strip()
                ingredient_name = ingredient_name.strip() 
                common_ingredient, confidence = predict(ingredient_name)
                common_ingredient_obj = CommonIngredient.objects.get(label=common_ingredient)
                # uci = UserCommonIngredient.objects.get(user=user, common_ingredient=common_ingredient)
                val = {'unit_type': unit, 'units': unit_value, 'name': ingredient_name,
                'confidence': confidence, 'common_ingredient': common_ingredient_obj, 'user': user}
                ing = Ingredient(**val)
                ing.save()
                # ing.user_common_ingredient.set(uci)
                ingredients.append(ing)
                common_ingredients.append(common_ingredient_obj)
            recipe = {'name': name, 'user': user}
            rec_obj = Recipe(**recipe)
            rec_obj.save()
            rec_obj.ingredients.set(ingredients)
            rec_obj.common_ingredients.set(common_ingredients)
            if _idx_ % 100 == 0:
                N = len(recipes[:1000])
                rem = N - _idx_
                print(f'{rem} remaining...')
            # print(f'Recipe {rec_obj.name} ({rec_obj.id}) saved!')
        except Exception as e:
            print(f'Error {e}')

import random
from recipeai.recipes.models import UserCommonIngredient 
from recipeai.recipes.models import UserIngredientCommonIngredient 
from recipeai.recipes.models import Ingredient 
from recipeai.users.models import User
from recipeai.recipes.models import Recipe


aarons = User.objects.filter(username__contains='aaron-')
ingredinets = list(Ingredient.objects.all())
# user_id = '85ec3e6a-35f8-4618-b854-e68f1cf25659'
for user in aarons[2:]:
    num_ingredients = random.randint(0, 100)
    my_ings = set()
# user = User.objects.get(id=user_id)

    ings = [x for x in ingredients if random.random() < .2]
    for i in ings:
        if i.common_ingredient not in my_ings and random.random() < .4:
            if len(my_ings) < num_ingredients:
                try:
                    uci = UserCommonIngredient(**{'user': user,'common_ingredient': i.common_ingredient})
                    uci.save()
                    uici = UserIngredientCommonIngredient(**{'user': user,'common_ingredient': i.common_ingredient, 'recipe_ingredient': i})
                    # uci.save()
                    uici.save()
                    my_ings.add(i.common_ingredient)
                except:
                    print('err')
    print('aaron finished')

