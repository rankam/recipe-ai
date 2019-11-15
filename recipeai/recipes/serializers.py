from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from recipeai.recipes.models import CommonIngredient, Ingredient, Recipe, Instruction
from recipeai.users.serializers import UserSerializer

class CommonIngredientSerializer(ModelSerializer):

    class Meta:
        model = CommonIngredient
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    name = serializers.CharField()
    units = serializers.CharField()
    unit_type = serializers.CharField()
    is_available = serializers.BooleanField()
    confidence = serializers.FloatField(required=False)
    common_ingredient = serializers.CharField(required=False)

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True) 
    user = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class InstructionSerializer(ModelSerializer):

    class Meta:
        model = Instruction
        fields = '__all__'
