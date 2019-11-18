from django.db import models
from ..users.models import User
from .ingredient_classifier import predict

class CommonIngredient(models.Model):
    __tablename__ = 'common_ingredient'

    label = models.CharField(max_length=160, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserCommonIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    common_ingredient = models.ForeignKey(CommonIngredient, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)

class Ingredient(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    units = models.CharField(max_length=160)
    unit_type = models.CharField(max_length=160)
    confidence = models.FloatField()
    user_common_ingredient = models.ManyToManyField(UserCommonIngredient)
    common_ingredient = models.ForeignKey(CommonIngredient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.common_ingredient_id, self.confidence = predict(self.name)
        super(Ingredient, self).save(*args, **kwargs)
        uci = UserCommonIngredient.objects.get(common_ingredient_id=self.common_ingredient_id,
                user_id=self.user.id)
        self.user_common_ingredient.add(uci) 

class Recipe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    ingredients = models.ManyToManyField(Ingredient)
    common_ingredients = models.ManyToManyField(CommonIngredient)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Instruction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    order = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

