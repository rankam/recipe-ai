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

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/v1/commoningredient/(?P<id>[0-9]+)$', recipes_views.CommonIngredientAPIView.as_view()),
    url(r'^api/v1/commoningredient/$', recipes_views.CommonIngredientAPIListView.as_view()),
  
    url(r'^api/v1/usercommoningredient/(?P<id>[0-9]+)$', recipes_views.UserCommonIngredientAPIView.as_view()),
    url(r'^api/v1/usercommoningredient/$', recipes_views.UserCommonIngredientAPIListView.as_view()),
  
    url(r'^api/v1/ingredient/(?P<id>[0-9]+)$', recipes_views.IngredientAPIView.as_view()),
    url(r'^api/v1/ingredient/$', recipes_views.IngredientAPIListView.as_view()),
  
    url(r'^api/v1/recipe/(?P<id>[0-9]+)$', recipes_views.RecipeAPIView.as_view()),
    url(r'^api/v1/recipe/$', recipes_views.RecipeAPIListView.as_view()),
  
    url(r'^api/v1/instruction/(?P<id>[0-9]+)$', recipes_views.InstructionAPIView.as_view()),
    url(r'^api/v1/instruction/$', recipes_views.InstructionAPIListView.as_view()),

    url(r'^api/v1/recipes-user-common-ingredients/$', recipes_views.RecipeUserCommonIngredientAPIView.as_view()),
    url(r'^api/v1/available-recipes/$', recipes_views.AvailableRecipeIngredientUserCommonIngredientAPIView.as_view()),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
