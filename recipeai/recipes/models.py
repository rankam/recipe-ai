from django.db import models
from django.contrib.postgres.search import SearchVectorField
from ..users.models import User
from .ingredient_classifier import predict
import logging


class CommonIngredient(models.Model):
    label = models.CharField(max_length=160, primary_key=True)
    display_name = models.CharField(max_length=160, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
  
    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.label_to_display_name()
        super(CommonIngredient, self).save(*args, **kwargs)

    def label_to_display_name(self):
        return self.label.replace('__label__', '').replace('-', ' ').title()


class Nutrient(models.Model):
    name = models.CharField(max_length=160, unique=True)
    unit_type = models.CharField(max_length=160)


class CommonIngredientNutrient(models.Model):
    common_ingredient = models.ForeignKey(CommonIngredient,
            on_delete=models.CASCADE)
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    amount = models.FloatField()


    class Meta:
        db_table = 'recipes_common_ingredient_nutrient'
        constraints = [
            models.UniqueConstraint(fields=['nutrient', 'common_ingredient'], name='nutrient_common_ingredient'),
        ]          

class UserCommonIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    common_ingredient = models.ForeignKey(CommonIngredient, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'common_ingredient'], name='user_common_ingredient'),
        ]    

class UserIngredientCommonIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    common_ingredient = models.ForeignKey(CommonIngredient, on_delete=models.CASCADE)
    recipe_ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)

class Ingredient(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    units = models.CharField(max_length=160)
    unit_type = models.CharField(max_length=160)
    confidence = models.FloatField()
    user_common_ingredient = models.ManyToManyField(UserCommonIngredient)
    user_ingredient_common_ingredient = models.ManyToManyField(UserIngredientCommonIngredient)
    common_ingredient = models.ForeignKey(CommonIngredient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.common_ingredient_id, self.confidence = predict(self.name)
        super(Ingredient, self).save(*args, **kwargs)        
        try:
            uci = UserCommonIngredient.objects.get(common_ingredient_id=self.common_ingredient_id,
                user_id=self.user.id)
            self.user_common_ingredient.add(uci) 
            # uici = UserIngredientCommonIngredient(**{
            #     'user': self.user,
            #     'common_ingredient': self.common_ingredient_id, 
            #     'recipe_ingredient': self.id})

        except Exception as e:
            x = 1

class Recipe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    ingredients = models.ManyToManyField(Ingredient, null=True)
    common_ingredients = models.ManyToManyField(CommonIngredient, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_vector = SearchVectorField(null=True)
  


class Instruction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    order = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


