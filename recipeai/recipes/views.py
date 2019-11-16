from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from recipeai.recipes.serializers import CommonIngredientSerializer
from recipeai.recipes.serializers import UserCommonIngredientSerializer, IngredientSerializer, RecipeSerializer
from recipeai.recipes.serializers import InstructionSerializer, RecipeIngredientUserCommonIngredientSerializer
from recipeai.recipes.serializers import AvailableRecipeIngredientUserCommonIngredientSerializer
from recipeai.recipes.models import CommonIngredient, UserCommonIngredient, Ingredient, Recipe, Instruction
from .queries import fetch_recipes_by_user
from .queries import fetch_available_recipes
import sys, os


class AvailableRecipeIngredientUserCommonIngredientAPIView(APIView):
    def get(self, request):
        try:
            missing_ingredients_limit = int(request.query_params.get('missing_ingredients_limit', 1))
            items = fetch_available_recipes(request.user.id, missing_ingredients_limit)
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = AvailableRecipeIngredientUserCommonIngredientSerializer(data=result_page, many=True)
            if serializer.is_valid():
                return paginator.get_paginated_response(serializer.data)
            return Response(status=404)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=404)


class RecipeUserCommonIngredientAPIView(APIView):
    def get(self, request):
        try:
            items = fetch_recipes_by_user(request.user.id)
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = RecipeIngredientUserCommonIngredientSerializer(data=result_page, many=True)
            if serializer.is_valid():
                return paginator.get_paginated_response(serializer.data)
            return Response(status=404)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=404)

class CommonIngredientAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = CommonIngredient.objects.get(pk=id)
            serializer = CommonIngredientSerializer(item)
            return Response(serializer.data)
        except CommonIngredient.DoesNotExist:
            return Response(status=404)

    def put(self, request, id, format=None):
        try:
            item = CommonIngredient.objects.get(pk=id)
        except CommonIngredient.DoesNotExist:
            return Response(status=404)
        serializer = CommonIngredientSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id, format=None):
        try:
            item = CommonIngredient.objects.get(pk=id)
        except CommonIngredient.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class CommonIngredientAPIListView(APIView):

    def get(self, request, format=None):
        items = CommonIngredient.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = CommonIngredientSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = CommonIngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserCommonIngredientAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = UserCommonIngredient.objects.get(pk=id)
            serializer = UserCommonIngredientSerializer(item)
            return Response(serializer.data)
        except UserCommonIngredient.DoesNotExist:
            return Response(status=404)

    def put(self, request, id, format=None):
        try:
            item = UserCommonIngredient.objects.get(pk=id)
        except UserCommonIngredient.DoesNotExist:
            return Response(status=404)
        serializer = UserCommonIngredientSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id, format=None):
        try:
            item = UserCommonIngredient.objects.get(pk=id)
        except UserCommonIngredient.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class UserCommonIngredientAPIListView(APIView):

    def get(self, request, format=None):
        items = UserCommonIngredient.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = UserCommonIngredientSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = UserCommonIngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class IngredientAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = Ingredient.objects.get(pk=id)
            serializer = IngredientSerializer(item)
            return Response(serializer.data)
        except Ingredient.DoesNotExist:
            return Response(status=404)

    def put(self, request, id, format=None):
        try:
            item = Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            return Response(status=404)
        serializer = IngredientSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id, format=None):
        try:
            item = Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class IngredientAPIListView(APIView):

    def get(self, request, format=None):
        items = Ingredient.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = IngredientSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class RecipeAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = Recipe.objects.get(pk=id)
            serializer = RecipeSerializer(item)
            return Response(serializer.data)
        except Recipe.DoesNotExist:
            return Response(status=404)

    def put(self, request, id, format=None):
        try:
            item = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            return Response(status=404)
        serializer = RecipeSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id, format=None):
        try:
            item = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class RecipeAPIListView(APIView):

    def get(self, request, format=None):
        user_id = request.user.id
        if user_id:
            items = Recipe.objects.filter(ingredients__user_common_ingredient__user_id=user_id)
        else:
            items = Recipe.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = RecipeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class InstructionAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = Instruction.objects.get(pk=id)
            serializer = InstructionSerializer(item)
            return Response(serializer.data)
        except Instruction.DoesNotExist:
            return Response(status=404)

    def put(self, request, id, format=None):
        try:
            item = Instruction.objects.get(pk=id)
        except Instruction.DoesNotExist:
            return Response(status=404)
        serializer = InstructionSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id, format=None):
        try:
            item = Instruction.objects.get(pk=id)
        except Instruction.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class InstructionAPIListView(APIView):

    def get(self, request, format=None):
        items = Instruction.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = InstructionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = InstructionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
