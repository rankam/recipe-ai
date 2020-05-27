import json
import string
from ..ingredient_classifier import predict
from recipeai.recipes.models import CommonIngredient , UserCommonIngredient
from recipeai.recipes.models import Ingredient 
from recipeai.users.models import User
from recipeai.recipes.models import Recipe
import re

TEST_RESULTS_PATH = '/users/aaronrank/Developer/recipe-ai/recipeai/recipes/ocr/ocado_results.json'

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

def load_text():
    with open(TEST_RESULTS_PATH, 'r') as f:
        text = json.loads(f.read())
    return text['ParsedResults'][0]['ParsedText']


def parse_and_add_user_common_ingredients(user_id, text=None):
    user = User.objects.get(id=user_id)
    if text is None:
        text = load_text()
    days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    'Friday', 'Saturday']
    start = False
    start_word = 'livered Price'
    skip_use_by = 'Use by'
    skip_use_by_date = "Products with no 'use-by' date"
    lines = text.split('\r\n')
    ingredients = []
    user_common_ingredients = []
    skips = []
    patterns = [        
            re.compile(r"^eat "),
            re.compile(r"^now "),
            re.compile(r"^essential "),
            re.compile(r"^british "),
            re.compile(r" british "),
            re.compile(r" english "),
            re.compile(r"^english "),
            re.compile(r"^waitrose "),
            re.compile(r"^reduced fat ")
    ]
    for i, line in enumerate(lines):
        if start_word.lower() in line.lower() and not start:
            print(f'starting after line {i}')
            start = True
            continue
        if not start:
            continue
        if skip_use_by.lower() in line.lower():
            continue
        if skip_use_by_date.lower() in line.lower():
            continue
        if len(line.split()) == 1:
            continue
        unit = ''
        unit_value = ''
        ingredient_name = ''
        line = line.lower().replace("waitrose", "")
        line = line.lower().replace(" eat ", " ")
        line = line.lower().replace(" now ", " ")
        line = line.lower().replace(" essential ", " ")
        line = line.lower().replace(" reduced fat ", " ")
        line = line.strip()
        tokens = line.split()
        for token in tokens:
            for pattern in patterns:
                token = re.sub(pattern, '', token)
            token = token.strip()
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
        common_ingredient, confidence = predict(ingredient_name.lower())
        if confidence < .9:
            skips.append({'conf': confidence, 'name': ingredient_name,
                'common_ing': common_ingredient})
            continue
        common_ingredient_obj = CommonIngredient.objects.get(label=common_ingredient)
        uci = UserCommonIngredient.objects.get(user=user, common_ingredient=common_ingredient)
        val = {'unit_type': unit, 'units': unit_value, 'name': ingredient_name,
        'confidence': confidence, 'common_ingredient': common_ingredient_obj, 'user': user}
        ing = Ingredient(**val)
        ing.save()
        # ing.user_common_ingredient.set(uci)
        ingredients.append(ing)
        uci.is_available = True
        uci.save(update_fields=["is_available"])
        user_common_ingredients.append(uci)
    return user_common_ingredients




import PyPDF2
import string






def percent_upper(text):
    '''
    returns the number of uppercase strings / the number of total strings
    '''
    text = text.replace(' ', '').strip()
    N = 0
    D = 0
    for char in text:
        if char.isspace() or char.isnumeric() or char in string.punctuation:
            continue
        D += 1
        if char.isupper():
            N += 1
    if D == 0 or D < 4:
        return 0
    return round(N / D, 2)


def strip_ending_price(text):
    pattern = re.compile(r'\(£[0-9]+.*\)')
    match = re.search(pattern, text)
    if match:
        return text[:match.start()].strip()
    return text

def parse_ingredient_text(text):
    discard_word_patterns = [
            re.compile(r"^eat "),
            re.compile(r" eat "),
            re.compile(r" now "),
            re.compile(r"^now "),
            re.compile(r"^essential "),
            re.compile(r" essential "),
            re.compile(r"^british "),
            re.compile(r" british "),
            re.compile(r" english "),
            re.compile(r"^english "),
            re.compile(r"^waitrose "),
            re.compile(r" waitrose "),
            re.compile(r"^reduced fat ") ,
            re.compile(r" reduced fat ") 
    ] 
    text = text.lower()  
    words = text.split(" ")
    units = ''
    unit_type = ''
    ingredient_name = ''
    if words[-1][0].isnumeric():
        last_word = words[-1]
        for i,char in enumerate(last_word):
            if char.isnumeric() or char == '.':
                units += char
            else:
                unit_type = last_word[i:]
                break
        ingredient_name = ' '.join(words[:-1])
    else:
        units = '1'
    ingredient_name_for_prediction = ingredient_name
    for discard_pattern in discard_word_patterns:
        ingredient_name_for_prediction = re.sub(discard_pattern, '', ingredient_name_for_prediction)
    return {
            'ingredient_name_for_prediction': ingredient_name_for_prediction,
            'ingredient_name': ingredient_name,
            'unit_type': unit_type,
            'units': units
        }



pdf_path = '/users/aaronrank/developer/recipe-ai/recipeai/recipes/ocr/ocado.pdf'
pdfFileObj = open(pdf_path, 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)    

items = []
prev_item_was_upper = False
text = []
product_use_by_label = ''
offers_savings_count = 0
for i in range(pdfReader.numPages):
    pageObj = pdfReader.getPage(i)
    page_text = pageObj.extractText().split('\n')
    text.extend(page_text)
for item in text:
    item = strip_ending_price(item)
    if item.startswith("Products with"):
        product_use_by_label = item 
    if product_use_by_label == "Products with no 'use-by' date":
        continue
    if 'Offers savings' in item:
        offers_savings_count += 1
        if offers_savings_count > 1:
            break
    if prev_item_was_upper and percent_upper(item) > .8:
        prev_item = items[-1]
        new_item = f'{prev_item} {item}'
        new_item = strip_ending_price(new_item)
        items[-1] = new_item
        prev_item_was_upper = True
    elif percent_upper(item) > .8:
        items.append(item)
        prev_item_was_upper = True
    else:
        prev_item_was_upper = False

predictions = []
for item in items:
    result = parse_ingredient_text(item)
    common_ingredient, confidence = predict(result['ingredient_name_for_prediction'])
    result['common_ingredient_id'] = common_ingredient 
    result['confidence'] = confidence
    predictions.append(result)








