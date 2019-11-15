from django.conf import settings
from django.conf.urls import url
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet
from .recipes.views import CommonIngredientAPIView, CommonIngredientAPIListView
from .recipes.views import IngredientAPIListView, IngredientAPIView
from .recipes.views import RecipeAPIView, RecipeAPIListView
from .recipes.views import InstructionAPIListView, InstructionAPIView
from .recipes.views import AvailableRecipesAPIView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/commoningredient/(?P<id>[0-9]+)$', CommonIngredientAPIView.as_view()),
    url(r'^api/v1/commoningredient/$', CommonIngredientAPIListView.as_view()),
    url(r'^api/v1/ingredient/(?P<id>[0-9]+)$', IngredientAPIView.as_view()),
    url(r'^api/v1/ingredient/$', IngredientAPIListView.as_view()),
    url(r'^api/v1/recipe/(?P<id>[0-9]+)$', RecipeAPIView.as_view()),
    url(r'^api/v1/recipe/$', RecipeAPIListView.as_view()),
    url(r'^api/v1/available-recipes/', AvailableRecipesAPIView.as_view()),
    url(r'^api/v1/instruction/(?P<id>[0-9]+)$', InstructionAPIView.as_view()),
    url(r'^api/v1/instruction/$', InstructionAPIListView.as_view()),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
