from rest_framework.serializers import ModelSerializer
from recipeai.recipes.models import CommonIngredient, UserCommonIngredient, Ingredient, Recipe, Instruction,UserIngredientCommonIngredient
from rest_framework import serializers
from recipeai.users.serializers import UserSerializer



class CommonIngredientSearchSerializer(serializers.Serializer):

    label = serializers.CharField()
    display_name = serializers.CharField()
    created_at = serializers.DateTimeField()

    class Meta:
        fields = ('label', 'created_at', 'display_name')    

class UserCommonIngredientSearchSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    user = serializers.UUIDField()
    display_name = serializers.CharField()
    common_ingredient = serializers.CharField()

    class Meta:
        fields = ('id', 'user', 'common_ingredient', 'display_name')          

class CommonIngredientSerializer(ModelSerializer):
    nutrients = serializers.ListField(required=False, read_only=True)

    class Meta:
        model = CommonIngredient
        fields = '__all__'

class ClassifyIngredientAsCommonIngredientSerializer(serializers.Serializer):

    name = serializers.CharField()
    common_ingredient = serializers.DictField()
    confidence = serializers.FloatField()

    class Meta:
        fields = '__all__'


class PostUserCommonIngredientSerializer(ModelSerializer):
    class Meta:
        model = UserCommonIngredient
        fields = '__all__'


class UserCommonIngredientSerializer(ModelSerializer):
    common_ingredient = CommonIngredientSerializer(required=False)

    class Meta:
        model = UserCommonIngredient
        # fields = ['id', 'user', 'common_ingredient']
        fields = '__all__'
        # depth = 1

class UserIngredientCommonIngredientSerializer(ModelSerializer):

    class Meta:
        model = UserIngredientCommonIngredient
        fields = '__all__'

class IngredientSerializer(ModelSerializer):
    confidence = serializers.FloatField(required=False)
    common_ingredient = CommonIngredientSerializer(read_only=True)
    user = UserSerializer(read_only=True, required=False)
    user_id = serializers.UUIDField()
    name = serializers.CharField()
    units = serializers.CharField()
    unit_type = serializers.CharField()
    user_common_ingredient = UserCommonIngredientSerializer(many=True,
            read_only=True, required=False)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'user_id', 'units', 'unit_type','common_ingredient','user','user_common_ingredient', 'confidence')


class RecipeSerializer(ModelSerializer):
    name = serializers.CharField()
    ingredients = IngredientSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField()
    user_common_ingredient = UserCommonIngredientSerializer(many=True,
            read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

class DeepRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe 
        fields = '__all__'
        depth = 3


class InstructionSerializer(ModelSerializer):

    class Meta:
        model = Instruction
        fields = '__all__'

class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    ingredients = serializers.ListField()
    calories = serializers.FloatField()

    class Meta:
        fields = ('name', 'id', 'ingredients', 'calories',)


class RecipeAddIngredientSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()

    class Meta:
        fields = '__all__'

    # def create(self, validated_data):
    #     return RecipeCommonIngredient.objects.create(**validated_data)

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
    user = UserSerializer(read_only=True, required=False)
    num_missing_ingredients = serializers.IntegerField()
    calories = serializers.FloatField(required=False)
    protein = serializers.FloatField(required=False)

    class Meta:
        fields = ('id',  'name',  'ingredients', 'num_missing_ingredients', 'calories','protein')

