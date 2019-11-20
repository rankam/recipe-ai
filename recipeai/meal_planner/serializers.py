from rest_framework.serializers import ModelSerializer
from recipeai.meal_planner.models import MealPlan, Meal, MealNutritionRequirement, DailyNutritionRequirement


class MealPlanSerializer(ModelSerializer):

    class Meta:
        model = MealPlan
        fields = '__all__'


class MealSerializer(ModelSerializer):

    class Meta:
        model = Meal
        fields = '__all__'


class MealNutritionRequirementSerializer(ModelSerializer):

    class Meta:
        model = MealNutritionRequirement
        fields = '__all__'


class DailyNutritionRequirementSerializer(ModelSerializer):

    class Meta:
        model = DailyNutritionRequirement
        fields = '__all__'
