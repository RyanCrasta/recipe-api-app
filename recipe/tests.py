from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import CustomUser

class RecipeAPITestCases(TestCase):
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

    def get_temporary_image(self):
        """Create a temporary image file."""
        image = Image.new('RGB', (100, 100))
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        return temp_file

    def login_functionality(self):
        user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post('/api/user/login/', user_data, format='json')
        access_token = response.data['tokens']['access']
        return access_token

    def create_recipe_functionality(self, access_token):
        image = self.get_temporary_image()
        data = {
            "title": "Test Recipe",
            "desc": "A short description of the test recipe.",
            "cook_time": "01:00:00",
            "ingredients": "Sugar, Flour, Butter",
            "procedure": "Mix and bake",
            "picture": SimpleUploadedFile(name='test_image.jpg', content=image.read(), content_type='image/jpeg'),
            "category.name": "Lunch",
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_create_response = self.client.post('/api/recipe/create/', data, format='multipart')
        return recipe_create_response

    def test_get_all_recipes(self):
        """Get all recipes /api/recipe/"""
        recipes_response = self.client.get('/api/recipe/')
        self.assertEqual(recipes_response.status_code, status.HTTP_200_OK)


    def test_create_recipe_successful(self):
        user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post('/api/user/login/', user_data, format='json')
        access_token = response.data['tokens']['access']

        image = self.get_temporary_image()

        data = {
            "title": "Test Recipe",
            "desc": "A short description of the test recipe.",
            "cook_time": "01:00:00",
            "ingredients": "Sugar, Flour, Butter",
            "procedure": "Mix and bake",
            "picture": SimpleUploadedFile(name='test_image.jpg', content=image.read(), content_type='image/jpeg'),
            "category.name": "Lunch",
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_create_response = self.client.post('/api/recipe/create/', data, format='multipart')
        self.assertEqual(recipe_create_response.status_code, status.HTTP_201_CREATED)

    def test_create_recipe_unsuccessful(self):
        """Test that recipe should not be created if payload invalid"""
        user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post('/api/user/login/', user_data, format='json')
        access_token = response.data['tokens']['access']

        image = self.get_temporary_image()

        data = {
            # "title": "Test Recipe",
            "desc": "A short description of the test recipe.",
            "cook_time": "01:00:00",
            "ingredients": "Sugar, Flour, Butter",
            "procedure": "Mix and bake",
            "picture": SimpleUploadedFile(name='test_image.jpg', content=image.read(), content_type='image/jpeg'),
            "category.name": "Lunch",
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_create_response = self.client.post('/api/recipe/create/', data, format='multipart')
        self.assertEqual(recipe_create_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_recipe_using_id(self):
        """Test get recipe using ID /api/recipe/id/"""
        access_token = self.login_functionality()
        recipe_create_response = self.create_recipe_functionality(access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_id = recipe_create_response.data['id']
        recipe_response = self.client.get(f'/api/recipe/{recipe_id}/')
        self.assertEqual(recipe_response.status_code, status.HTTP_200_OK)

    def test_edit_a_recipe_put(self):
        """Test edit a recipe using id (PUT) /api/recipe/id/"""
        access_token = self.login_functionality()
        recipe_create_response = self.create_recipe_functionality(access_token)
        recipe_id = recipe_create_response.data['id']

        image = self.get_temporary_image()

        data = {
            "title": "Test New Recipe",
            "desc": "A new description of new test recipe.",
            "cook_time": "09:00:00",
            "ingredients": "Milk, Sugar, Flour, Butter",
            "procedure": "Mix and bake",
            "picture": SimpleUploadedFile(name='test_image.jpg', content=image.read(), content_type='image/jpeg'),
            "category.name": "Dinner",
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_response = self.client.put(f'/api/recipe/{recipe_id}/', data, format='multipart')
        self.assertEqual(recipe_response.status_code, status.HTTP_200_OK)

    def test_edit_a_recipe_patch(self):
        """Test edit a recipe using id (PATCH) /api/recipe/id/"""
        access_token = self.login_functionality()
        recipe_create_response = self.create_recipe_functionality(access_token)
        recipe_id = recipe_create_response.data['id']

        image = self.get_temporary_image()

        data = {
            # "title": "Test New Recipe",
            "desc": "Brand new description",
            # "cook_time": "09:00:00",
            # "ingredients": "Milk, Sugar, Flour, Butter",
            # "procedure": "Mix and bake",
            # "picture": SimpleUploadedFile(name='test_image.jpg', content=image.read(), content_type='image/jpeg'),
            # "category.name": "Dinner",
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_response = self.client.patch(f'/api/recipe/{recipe_id}/', data, format='multipart')
        self.assertEqual(recipe_response.status_code, status.HTTP_200_OK)

    def test_delete_a_recipe_by_id(self):
        """Test delete a recipe by ID (DELETE)"""
        access_token = self.login_functionality()
        recipe_create_response = self.create_recipe_functionality(access_token)
        recipe_id = recipe_create_response.data['id']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_delete_response = self.client.delete(f'/api/recipe/{recipe_id}/')
        self.assertEqual(recipe_delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_like_a_recipe_by_id(self):
        """Test like a recipe by ID /api/recipe/:recipeID/like/"""
        access_token = self.login_functionality()
        recipe_create_response = self.create_recipe_functionality(access_token)
        recipe_id = recipe_create_response.data['id']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        recipe_like_response = self.client.post(f'/api/recipe/{recipe_id}/like/')
        self.assertEqual(recipe_like_response.status_code, status.HTTP_201_CREATED)

    def test_delete_a_recipe_like_by_id(self):
        """Delete recipe like by ID /api/recipe/:recipeID/like/"""
        access_token = self.login_functionality()
        recipe_create_response = self.create_recipe_functionality(access_token)
        recipe_id = recipe_create_response.data['id']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        #first like the recipe, to unlike it
        self.client.post(f'/api/recipe/{recipe_id}/like/')

        recipe_unlike_response = self.client.delete(f'/api/recipe/{recipe_id}/like/')
        self.assertEqual(recipe_unlike_response.status_code, status.HTTP_200_OK)