from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .serializers import MealSerializer 
from .serializers import MealPlanSerializer 
from .serializers import MealNutritionRequirementSerializer 
from .serializers import DailyNutritionRequirementSerializer 
from .models import Meal 
from .models import MealPlan 
from .models import MealNutritionRequirement 
from .models import DailyNutritionRequirement 


class MealViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves Meal accounts
    """
    queryset = Meal.objects.all()
    serializer_class = MealSerializer


class MealCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates Meal accounts
    """
    queryset = Meal.objects.all()
    serializer_class = MealSerializer 


class MealPlanViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves MealPlan accounts
    """
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer


class MealPlanCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates MealPlan accounts
    """
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer

class MealNutritionRequirementViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves MealNutritionRequirement accounts
    """
    queryset = MealNutritionRequirement.objects.all()
    serializer_class = MealNutritionRequirementSerializer


class MealNutritionRequirementCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates MealNutritionRequirement accounts
    """
    queryset = MealNutritionRequirement.objects.all()
    serializer_class = MealNutritionRequirementSerializer

class DailyNutritionRequirementViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves DailyNutritionRequirement accounts
    """
    queryset = DailyNutritionRequirement.objects.all()
    serializer_class = DailyNutritionRequirementSerializer


class DailyNutritionRequirementCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates DailyNutritionRequirement accounts
    """
    queryset = DailyNutritionRequirement.objects.all()
    serializer_class = DailyNutritionRequirementSerializer

