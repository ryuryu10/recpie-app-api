
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
  defaults = {
    'title': 'Sample Recipe Title',
    'time_minutes': 22,
    'price': Decimal('5.25'),
    'description': 'Sample Recipe Description',
    'link': 'http://example.com/'
  }
  defaults.update(params)

  reciple = Recipe.objects.create(user=user, **defaults)
  return reciple

class PublicRecipeAPITests(TestCase):

  def setUP(self):
    self.client = APIClient()
  
  def test_auth_required(self):
    res = self.client.get(RECIPES_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipleAPITests(TestCase):

  def setUp(self):
    self.client = APIClient()
    self.user = get_user_model().objects.create_user(
      'user@example.com',
      'testpass123',
    )
    self.client.force_authenticate(self.user)

  def test_retrive_recipes(self):
    create_recipe(user=self.user)
    create_recipe(user=self.user)
    
    res = self.client.get(RECIPES_URL)

    recipes = Recipe.objects.all().order_by('-id')
    serializers = RecipeSerializer(recipes, many=True)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializers.data)

  def test_recipe_list_limited_to_user(self):
    other_user = get_user_model().objects.create_user(
      'other@exmaple.com',
      'testpass123',
    )

    create_recipe(user=other_user)
    create_recipe(user=self.user)

    res = self.client.get(RECIPES_URL)

    recipes = Recipe.objects.filter(user=self.user)
    serializers = RecipeSerializer(recipes, many=True)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializers.data)