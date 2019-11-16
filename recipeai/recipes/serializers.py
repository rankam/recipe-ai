from rest_framework.serializers import ModelSerializer
from recipeai.recipes.models import CommonIngredient, UserCommonIngredient, Ingredient, Recipe, Instruction
from rest_framework import serializers
from recipeai.users.serializers import UserSerializer


class CommonIngredientSerializer(ModelSerializer):

    class Meta:
        model = CommonIngredient
        fields = '__all__'


class UserCommonIngredientSerializer(ModelSerializer):

    class Meta:
        model = UserCommonIngredient
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    confidence = serializers.FloatField(required=False)
    common_ingredient = CommonIngredientSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    user_common_ingredient = UserCommonIngredientSerializer(many=True,
            read_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    user_common_ingredient = UserCommonIngredientSerializer(many=True,
            read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class InstructionSerializer(ModelSerializer):

    class Meta:
        model = Instruction
        fields = '__all__'

class RecipeIngredientUserCommonIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.CharField()
    name = serializers.CharField()
    created_at = serializers.DateTimeField()
    ingredients = serializers.ListField() 
    user_common_ingredient = serializers.ListField()

    class Meta:
        fields = ('id', 'user_id', 'name', 'created_at', 'ingredients',
                'user_common_ingredient',)

class AvailableRecipeIngredientUserCommonIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    ingredients = serializers.ListField() 

    class Meta:
        fields = ('id',  'name',  'ingredients',)

