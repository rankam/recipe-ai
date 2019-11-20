import pandas as pd
import string
try:
    from .models import Nutrient, CommonIngredientNutrient, CommonIngredient
except ImportError:
    from recipeai.recipes.models import Nutrient, CommonIngredientNutrient, CommonIngredient

food = pd.read_csv('/Users/aaronrank/Downloads/FoodData_Central_csv_2019-10-11/food.csv')
food_nutrient = pd.read_csv('/Users/aaronrank/Downloads/FoodData_Central_csv_2019-10-11/food_nutrient.csv')
nutrient = pd.read_csv('/Users/aaronrank/Downloads/FoodData_Central_csv_2019-10-11/nutrient.csv')
nutrition = pd.merge(pd.merge(food, food_nutrient, on='fdc_id'), nutrient, left_on='nutrient_id', right_on='id')
legacy_foods = nutrition[nutrition['data_type'] == 'sr_legacy_food']

LABEL_PREFIX = '__label__'
filetxt = ''
KNOWN_UNITS = []
matches = []
nutrients_to_keep = ['Total lipid (fat)',  
'Protein',                             
'Sodium, Na',                          
'Carbohydrate, by difference',         
'Energy',                              
'Sugars, total including NLEA',        
'Fatty acids, total saturated',        
'Cholesterol',                         
'Fiber, total dietary',                
'Iron, Fe',                            
'Calcium, Ca',                         
'Fatty acids, total trans',            
'Vitamin C, total ascorbic acid',      
'Vitamin A, IU',                       
'Potassium, K',                         
'Fatty acids, total monounsaturated',   
'Fatty acids, total polyunsaturated',   
'Vitamin D',                            
'Niacin',                               
'Thiamin',                              
'Riboflavin',                           
'Phosphorus, P',                        
'Magnesium, Mg',                        
'Vitamin B-6',                          
'Zinc, Zn',                             
'Vitamin B-12',                         
'Folate, total',                        
'Copper, Cu',                           
'Water',                                
'Sugars, added',                        
'Folic acid',                           
'Selenium, Se']
for ingredient, unit_name, amount,nutrient_name in zip(legacy_foods.description,
        legacy_foods.unit_name, legacy_foods.amount, legacy_foods.name):
    target = ingredient.replace(',', '').replace("'", '').replace(';', '')
    _ingredient = ingredient
    for p in string.punctuation:
        target = target.replace(p, '')
        _ingredient = _ingredient.replace(p, '')
    tokens = _ingredient.split()
    ingredient_text = ''
    for token in tokens:
        if token.strip('s') not in KNOWN_UNITS and not token.strip().isnumeric() and token.strip():
            ingredient_text += f'{token} '
    ingredient_text = ingredient_text.strip()
    target = target.lower().replace(' ', '-')
    label = f'{LABEL_PREFIX}{target}'
    try:
        ci = CommonIngredient.objects.get(label=label)
        if nutrient_name in nutrients_to_keep:
            nut = Nutrient(name=nutrient_name, unit_type=unit_name)
            nut.save()
            print('nutrient saved')
            cin = CommonIngredientNutrient(common_ingredient=ci, nutrient=nut,
                    amount=amount)
            cin.save()
            print('common ingredient nutrient saved')
    except:
        continue


