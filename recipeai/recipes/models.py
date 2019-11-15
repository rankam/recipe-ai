from django.db import models
from ..users.models import User
from .ingredient_classifier import predict

class CommonIngredient(models.Model):
    __tablename__ = 'common_ingredient'

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    label = models.CharField(max_length=128)
    uuid = models.CharField(max_length=160)

class Ingredient(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    units = models.CharField(max_length=160)
    unit_type = models.CharField(max_length=160)
    is_available = models.BooleanField(default=False)
    confidence = models.FloatField()
    common_ingredient = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.common_ingredient, self.confidence = predict(self.name)
        super(Ingredient, self).save(*args, **kwargs)


class Recipe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160)
    ingredients = models.ManyToManyField(Ingredient)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Instruction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    order = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

