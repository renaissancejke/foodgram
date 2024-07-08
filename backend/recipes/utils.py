import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import IngredientRecipe, UserShoppingCart


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def get_ingridients_in_shop_cart(user):
    ingredient_details = {}
    recipe_ids = UserShoppingCart.objects.filter(
        user=user).values_list('recipe', flat=True)
    recipe_ingredients = IngredientRecipe.objects.filter(
        recipe_id__in=recipe_ids
    ).select_related('ingredients')
    for ingredient_recipe in recipe_ingredients:
        ingredient_name = ingredient_recipe.ingredients.name
        amount = ingredient_recipe.amount
        unit = ingredient_recipe.ingredients.measurement_unit
        if ingredient_name in ingredient_details:
            ingredient_details[ingredient_name]['amount'] += amount
        else:
            ingredient_details[ingredient_name] = {
                'amount': amount, 'unit': unit
            }
    return ingredient_details
