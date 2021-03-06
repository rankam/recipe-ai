from django.conf.urls import include, url
try:
  from django.conf.urls import patterns
except ImportError:
  pass
import django
from django.contrib import admin
from recipeai.recipes import views

if django.VERSION[1] < 10:
  urlpatterns = patterns('',
  
    url(r'^commoningredient/(?P<id>[0-9]+)$', views.CommonIngredientAPIView.as_view()),
    url(r'^commoningredient/$', views.CommonIngredientAPIListView.as_view()),
  
    url(r'^usercommoningredient/(?P<id>[0-9]+)$', views.UserCommonIngredientAPIView.as_view()),
    url(r'^usercommoningredient/$', views.UserCommonIngredientAPIListView.as_view()),
  
    url(r'^ingredient/(?P<id>[0-9]+)$', views.IngredientAPIView.as_view()),
    url(r'^ingredient/$', views.IngredientAPIListView.as_view()),
  
    url(r'^recipe/(?P<id>[0-9]+)$', views.RecipeAPIView.as_view()),
    url(r'^recipe/$', views.RecipeAPIListView.as_view()),
  
    url(r'^instruction/(?P<id>[0-9]+)$', views.InstructionAPIView.as_view()),
    url(r'^instruction/$', views.InstructionAPIListView.as_view()),
  
  )
else:
  urlpatterns = [
  
    url(r'^api/v1/commoningredient/(?P<id>[0-9]+)$', views.CommonIngredientAPIView.as_view()),
    url(r'^api/v1/commoningredient/$', views.CommonIngredientAPIListView.as_view()),
  
    url(r'^api/v1/usercommoningredient/(?P<id>[0-9]+)$', views.UserCommonIngredientAPIView.as_view()),
    url(r'^api/v1/usercommoningredient/$', views.UserCommonIngredientAPIListView.as_view()),
  
    url(r'^api/v1/ingredient/(?P<id>[0-9]+)$', views.IngredientAPIView.as_view()),
    url(r'^api/v1/ingredient/$', views.IngredientAPIListView.as_view()),
  
    url(r'^api/v1/recipe/(?P<id>[0-9]+)$', views.RecipeAPIView.as_view()),
    url(r'^api/v1/recipe/$', views.RecipeAPIListView.as_view()),
  
    url(r'^api/v1/instruction/(?P<id>[0-9]+)$', views.InstructionAPIView.as_view()),
    url(r'^api/v1/instruction/$', views.InstructionAPIListView.as_view()),
  
  ]
