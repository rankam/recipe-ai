from django.conf import settings
from django.conf.urls import url
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet
from .recipes import views as recipes_views
from .meal_planner.views import MealViewSet
from .meal_planner.views import MealCreateViewSet
from .meal_planner.views import MealPlanViewSet
from .meal_planner.views import MealPlanCreateViewSet
from .meal_planner.views import MealNutritionRequirementViewSet
from .meal_planner.views import MealNutritionRequirementCreateViewSet
from .meal_planner.views import DailyNutritionRequirementViewSet
from .meal_planner.views import DailyNutritionRequirementCreateViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)
router.register(r'add-usercommoningredient',
        recipes_views.UserCommonIngredientAPIListView,
        basename='UserCommonIngredient')
router.register('meal', MealViewSet)
router.register('meal', MealCreateViewSet)
router.register('meal-plan', MealPlanViewSet)
router.register('meal-plan', MealPlanCreateViewSet)
router.register('meal-nutrition-requirement', MealNutritionRequirementViewSet)
router.register('meal-nutrition-requirement', MealNutritionRequirementCreateViewSet)
router.register('daily-nutrition-requirement', DailyNutritionRequirementViewSet)
router.register('daily-nutrition-requirement', DailyNutritionRequirementCreateViewSet)
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    url(r'^api/v1/classify-ingredient-common-ingredient/$', recipes_views.ClassifyIngredientAsCommonIngredientView.as_view()),


    url(r'^api/v1/usercommoningredients/$', recipes_views.UserCommonIngredientSearchAPIView.as_view()),
    url(r'^api/v1/search-user-common-ingredients/$', recipes_views.UserCommonIngredientSearchAPIView.as_view()),
    url(r'^api/v1/search-common-ingredients/$', recipes_views.CommonIngredientSearchAPIView.as_view()),
    url(r'^api/v1/commoningredient/<int:pk>/$', recipes_views.CommonIngredientAPIView.as_view()),
    url(r'^api/v1/commoningredient/$', recipes_views.CommonIngredientSearchAPIView.as_view()),
  
    url(r'^api/v1/usercommoningredient/(?P<id>[0-9]+)/$', recipes_views.UserCommonIngredientAPIView.as_view()),
    # url(r'^api/v1/add-usercommoningredient/$', recipes_views.UserCommonIngredientAPIListView.as_view()),
  
    url(r'^api/v1/ingredient/(?P<id>[0-9]+)$', recipes_views.IngredientAPIView.as_view()),
    url(r'^api/v1/ingredient/$', recipes_views.IngredientAPIListView.as_view()),
  
    url(r'^api/v1/recipe/(?P<id>[0-9]+)$', recipes_views.RecipeAPIView.as_view()),
    url(r'^api/v1/recipe/$', recipes_views.RecipeAPIListView.as_view()),
    url(r'^api/v1/recipe/(?P<id>[0-9]+)/ingredient/$', recipes_views.RecipeIngredientApiView.as_view()),
  
    url(r'^api/v1/instruction/(?P<id>[0-9]+)$', recipes_views.InstructionAPIView.as_view()),
    url(r'^api/v1/instruction/$', recipes_views.InstructionAPIListView.as_view()),

    # returns all recipes with a list of ingredients that the user has - does not return the ingredients the user does not have
    url(r'^api/v1/recipes-user-common-ingredients/$', recipes_views.RecipeUserCommonIngredientAPIView.as_view()),
    url(r'^api/v1/available-recipes/$', recipes_views.AvailableRecipeIngredientUserCommonIngredientAPIView.as_view()),
    url(r'^api/v1/ocado-poc/$',recipes_views.OcadoPOCReceiptToUserCommonIngredientApiView.as_view()),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
