from django.db import models
from ..recipes.models import Recipe
from ..users.models import User



class MealPlan(models.Model):

    class Meta:
        db_table = 'meal_plan_meal_plan'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)
    created_at = models.DateTimeField(auto_now_add=True)

class Meal(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)
    type = models.CharField(max_length=160)
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class MealNutritionRequirement(models.Model):
    
    class Meta:
        db_table = 'meal_plan_meal_nutrition_requirement'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calorie_min = models.FloatField()
    calorie_max = models.FloatField()
    fats_min = models.FloatField()
    fats_max = models.FloatField()
    protein_min = models.FloatField()
    protein_max = models.FloatField()
    carbs_min = models.FloatField()
    carbs_max = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class DailyNutritionRequirement(models.Model):
    
    class Meta:
        db_table = 'meal_plan_daily_nutrition_requirement'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calorie_min = models.FloatField()
    calorie_max = models.FloatField()
    fats_min = models.FloatField()
    fats_max = models.FloatField()
    protein_min = models.FloatField()
    protein_max = models.FloatField()
    carbs_min = models.FloatField()
    carbs_max = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
