from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from recipeai.recipes.serializers import CommonIngredientSerializer,CommonIngredientSearchSerializer
from recipeai.recipes.serializers import UserCommonIngredientSerializer, IngredientSerializer, RecipeSerializer
from recipeai.recipes.serializers import InstructionSerializer, RecipeIngredientUserCommonIngredientSerializer, PostUserCommonIngredientSerializer
from recipeai.recipes.serializers import AvailableRecipeIngredientUserCommonIngredientSerializer,UserCommonIngredientSearchSerializer
from recipeai.recipes.models import CommonIngredient, UserCommonIngredient, Ingredient, Recipe, Instruction, CommonIngredientNutrient
from recipeai.users.models import User
from .queries import fetch_recipes_by_user, fetch_recipe_by_id
from .queries import fetch_available_recipes
from .queries import search_common_ingredients,search_user_common_ingredients
import sys, os
import json
from rest_framework import viewsets, mixins
from .ocr.ocado_to_ingredients import parse_and_add_user_common_ingredients
from django.views.decorators.csrf import csrf_exempt
from recipeai.users.serializers import UserSerializer
from recipeai.recipes.serializers import RecipeIngredientSerializer,ClassifyIngredientAsCommonIngredientSerializer,RecipeAddIngredientSerializer
from recipeai.recipes.ingredient_classifier import predict
from django.core import serializers

USER_ID = 'cdc1c86e-068a-45a0-95b8-22fdf54744c6'
USER = User.objects.get(id=USER_ID)


class ClassifyIngredientAsCommonIngredientView(APIView):

    def post(self, request):
        ingredient_name = request.data.get("name")
        common_ingredient_id, confidence = predict(ingredient_name)
        ci = CommonIngredient.objects.get(label=common_ingredient_id)
        ci_copy = ci.__dict__.copy()
        ci_copy.pop('_state')
        nutrients = []
        for cin in ci.commoningredientnutrient_set.all():
            nut = cin.nutrient.__dict__.copy()
            nut.pop('_state')
            nut['amount'] = cin.amount
            nutrients.append(nut)
        ci_copy['nutrients'] = nutrients
        serializer = ClassifyIngredientAsCommonIngredientSerializer(
                data={
                        'name': ingredient_name,
                        'common_ingredient': ci_copy,
                        'confidence': confidence
                }) 
        if serializer.is_valid():
            return Response(serializer.data)
        print(serializer.errors)
        return Response(status=404)




class RecipeIngredientApiView(APIView):

    def post(self, request, id):
        try:
            serializer = RecipeAddIngredientSerializer(data=request.data)
            if serializer.is_valid():
                recipe = Recipe.objects.get(id=id)
                recipe.ingredients.add(request.data['ingredient_id'])
                ingredient = Ingredient.objects.get(id=request.data['ingredient_id'])
                recipe.common_ingredients.add(ingredient.common_ingredient)
                recipe = fetch_recipe_by_id(USER_ID, recipe.id)
                response_ser = RecipeIngredientSerializer(data=recipe[0])
                if response_ser.is_valid():
                    return Response(response_ser.data)
                print(response_ser.errors)
            print(serializer.errors)
            return Response(status=404)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            return Response(status=404)

    def delete(self, request, id):
        try:
            ingredient_id = request.query_params.get('ingredient_id')
            recipe = Recipe.objects.get(id=id)
            recipe.ingredients.remove(ingredient_id)
            recipe = fetch_recipe_by_id(USER_ID, recipe.id)
            print(recipe[0])
            response_ser = RecipeIngredientSerializer(data=recipe[0])
            if response_ser.is_valid():
                print('everywhere')
                return Response(response_ser.data)
            print('ser', response_ser.errors)
            return Response(status=404)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            return Response(status=404)            


class OcadoPOCReceiptToUserCommonIngredientApiView(APIView):

    def post(self, request):
        try:
            items = parse_and_add_user_common_ingredients(request.user.id)
            serializer = UserCommonIngredientSerializer(data=items)
            if serializer.is_valid():
                return Response(serializer.data)
            return Response(status=404)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            return Response(status=404)



class LimitPageNumberPagination(PageNumberPagination):

    def __init__(self, n):
        self.page_size = n

class AvailableRecipeIngredientUserCommonIngredientAPIView(APIView):

    @csrf_exempt
    def get(self, request):        
        missing_ingredients_limit = int(request.query_params.get('missing-ingredients-limit', 3))
        confidence_level = request.query_params.get('confidence-level')
        search_term = request.query_params.get('searchTerm', 'empty')
        if confidence_level:
            confidence_level = float(confidence_level) / 100.00
        else:
            confidence_level = .0
        # items = fetch_available_recipes(request.user.id, confidence_level,
        #         missing_ingredients_limit)
        items = fetch_available_recipes(USER_ID, confidence_level,
                missing_ingredients_limit, search_term) 

        try:
            missing_ingredients_limit = int(request.query_params.get('missing-ingredients-limit', 3))
            confidence_level = request.query_params.get('confidence-level')
            search_term = request.query_params.get('searchTerm', 'empty')
            if confidence_level:
                confidence_level = float(confidence_level) / 100.00
            else:
                confidence_level = .0
            # items = fetch_available_recipes(request.user.id, confidence_level,
            #         missing_ingredients_limit)
            items = fetch_available_recipes(USER_ID, confidence_level,
                    missing_ingredients_limit, search_term) 
            user_ser = UserSerializer(USER)
            _items = []
            for item in items:
                item.update({'user': user_ser})
                _items.append(item)
            paginator = LimitPageNumberPagination(1000)
            result_page = paginator.paginate_queryset(_items, request)
            serializer = AvailableRecipeIngredientUserCommonIngredientSerializer(data=result_page, many=True)
            if serializer.is_valid():
                return paginator.get_paginated_response(serializer.data)
            print(serializer.errors)
            return Response(status=404)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=404)

class CommonIngredientSearchAPIView(APIView):

    def get(self, request):        
        try:
            search_term = request.query_params.get('searchTerm')        
            items = search_common_ingredients(search_term)
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = CommonIngredientSearchSerializer(data=result_page, many=True)
            if serializer.is_valid():
                return paginator.get_paginated_response(serializer.data)
            print(serializer.errors)
            return Response(status=404)             
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=404)

class UserCommonIngredientSearchAPIView(APIView):

    def get(self, request): 
        try:
            search_term = request.query_params.get('searchTerm') 
            items = search_user_common_ingredients(USER_ID, search_term)
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = UserCommonIngredientSearchSerializer(data=result_page, many=True)
            if serializer.is_valid():
                return paginator.get_paginated_response(serializer.data)                   
            print(serializer.errors)
            return Response(status=404)             
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=404)            

class RecipeUserCommonIngredientAPIView(APIView):

    def get(self, request):
        try:
            items = fetch_recipes_by_user(USER_ID)
            # items = fetch_recipes_by_user(request.user.id)
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = RecipeIngredientUserCommonIngredientSerializer(data=result_page, many=True)
            if serializer.is_valid():
                return paginator.get_paginated_response(serializer.data)
            print(serializer.errors)
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


class LimitPageNumberPagination(PageNumberPagination):

    def __init__(self, n):
        self.page_size = n


class UserCommonIngredientAPIListView( viewsets.GenericViewSet):

    serializer_class = UserCommonIngredientSerializer

    def list(self, request, format=None):
        # limit = request.query_params.get('limit', 10)
        try:
            if request.query_params.get('is-available'):
                is_available = json.loads(request.query_params.get('is-available'))
                # items = UserCommonIngredient.objects.filter(#user_id=request.user.id,
                #                                             user_id=USER_ID,
                #                                             is_available=is_available
                #                                             )
                items = self.get_queryset()
            else:
                items = self.get_queryset()
                    #user_id=request.user.id)
            # paginator = LimitPageNumberPagination(limit)
            paginator= PageNumberPagination()
            result_page = paginator.paginate_queryset(items, request)
            serializer = UserCommonIngredientSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=404)            

    def get_queryset(self):
        return UserCommonIngredient.objects.filter(
            user_id=USER_ID
            # user_id=self.request.user.id
            ).order_by('-id')

    def get(self, request, format=None):
        return self.list(request, format)

    def post(self, request, format=None):
        try:
            request.data['user'] = USER_ID
            serializer = PostUserCommonIngredientSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            print(serializer.errors)
            return Response(serializer.errors, status=400)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response(status=400)            


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
        # print(request.data)
        request.data['user'] = USER
        # request.data['user'] = request.user
        request.data['user_id'] = USER_ID
        # request.data['user_id'] = request.user.id

        serializer = IngredientSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            serializer.save()
            cins = CommonIngredientNutrient.objects.filter(common_ingredient_id=serializer.data['common_ingredient']['label'])
            nutrients = []
            for cin in cins:
                nutrient = {
                'id': cin.nutrient_id,
                'name': cin.nutrient.name,
                'amount': cin.amount,
                'unit_type': cin.nutrient.unit_type,
                }
                nutrients.append(nutrient)
            serializer.data['common_ingredient'].update({'nutrients': nutrients})
            return Response(serializer.data, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)


class RecipeAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = fetch_recipe_by_id(USER_ID, id)
            # item = Recipe.objects.get(pk=id)
            serializer = RecipeIngredientSerializer(item[0])
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
        # user_id = request.user.id
        user_id = USER_ID
        if user_id:
            items = Recipe.objects.filter(ingredients__user_common_ingredient__user_id=user_id).distinct()
        else:
            items = Recipe.objects.distinct()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = RecipeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        request.data['user_id'] = USER.id
        request.data['user'] = USER
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

