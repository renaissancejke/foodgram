import base64

from django.core.files.base import ContentFile
from django.db.models import Sum, F
from rest_framework import serializers

from recipes.models import IngredientRecipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def get_ingridients_in_shop_cart(user):
    ingredient_details = (
        IngredientRecipe.objects.filter(recipe__usershoppingcart__user=user)
        .values('ingredients__name', 'ingredients__measurement_unit')
        .annotate(
            amount=Sum(F('amount')),
        )
        .order_by('ingredients__name')
    )

    return {
        item['ingredients__name']: {
            'amount': item['amount'],
            'unit': item['ingredients__measurement_unit']
        }
        for item in ingredient_details
    }
