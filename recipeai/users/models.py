import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        should_create_user_common_ingredients = False
        print(self._state.adding)
        if self._state.adding is True:
            should_create_user_common_ingredients = True
            print('creating ucis')
        else:
            print('not creating ucis')
        super(User, self).save(*args, **kwargs)
        if should_create_user_common_ingredients:
            from ..recipes.models import UserCommonIngredient, CommonIngredient
            for ci in CommonIngredient.objects.all():
                uci = UserCommonIngredient(user=self, common_ingredient=ci)
                uci.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
