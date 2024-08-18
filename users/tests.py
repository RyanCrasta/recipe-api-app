from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from .models import CustomUser, Profile
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import tempfile

class UserAPITestCase(TestCase):
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Create a user for login tests
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)

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
        return response.data

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


    def test_user_registration(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post('/api/user/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        """Test the API can log in a user with correct credentials"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post('/api/user/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bad_user_login(self):
        """Test the API cannot log in a user with wrong credentials"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass1'
        }
        response = self.client.post('/api/user/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        """Test that the logout API successfully blacklists a valid refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post('/api/user/logout/', data={'refresh': str(self.refresh_token)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_with_invalid_token(self):
        """Test that the logout API returns a 400 status for an invalid refresh token."""
        invalid_token = 'invalidtoken'
        response = self.client.post(self.logout_url, data={'refresh': invalid_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_change_put(self):
        """Test password change API /api/user/password/change/"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post('/api/user/login/', data, format='json')

        password_data = {
            'old_password': 'testpass',
            'new_password': 'newtestpass'
        }

        access_token = response.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        change_pass_response = self.client.put('/api/user/password/change/', password_data, format='json')
        self.assertEqual(change_pass_response.status_code, status.HTTP_200_OK)

    def test_get_user_profile(self):
        """Test Get user profile /api/user/profile/"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_user_profile_put(self):
        """Test Edit (PUT) user profile /api/user/profile/"""
        access_token = self.login_functionality()['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        created_recipe_response = self.create_recipe_functionality(access_token)
        recipe_id = created_recipe_response.data['id']
        data = {
            "bio": "I am foodie",
            "bookmarks": [recipe_id]
        }
        response = self.client.put('/api/user/profile/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        wrong_data = {
            "bio": "Sugar, spice, and everything nice",
            "bookmarks": []
        }
        second_response = self.client.put('/api/user/profile/', wrong_data, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_user_profile_patch(self):
        """Test Edit (PATCH) user profile /api/user/profile/"""
        access_token = self.login_functionality()['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        created_recipe_response = self.create_recipe_functionality(access_token)
        recipe_id = created_recipe_response.data['id']
        data = {
            "bio": "I am foodie",
            "bookmarks": [recipe_id]
        }
        response = self.client.patch('/api/user/profile/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        wrong_data = {
            "bio": "Sugar, spice, and everything nice",
            "bookmarks": []
        }
        second_response = self.client.patch('/api/user/profile/', wrong_data, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_avatar(self):
        """Test Get user avtar /api/user/profile/avatar/"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get('/api/user/profile/avatar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bookmarks(self):
        """Test Get user bookmarks /api/user/profile/:userid/bookmarks/"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post('/api/user/login/', data, format='json')
        access_token = response.data['tokens']['access']
        user_id = response.data['id']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        get_bookmark_response = self.client.get(f'/api/user/profile/{user_id}/bookmarks/')
        self.assertEqual(get_bookmark_response.status_code, status.HTTP_200_OK)

    def test_add_a_bookmark_post(self):
        """Test Add a bookmark (POST) /api/user/profile/:userid/bookmarks/"""
        user_logged_in_data = self.login_functionality()
        userID = user_logged_in_data['id']
        access_token = user_logged_in_data['tokens']['access']

        recipe_response_data = self.create_recipe_functionality(access_token).data

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        recipe_data_payload = {
            "id": recipe_response_data['id']
        }
        get_bookmark_response = self.client.post(f'/api/user/profile/{userID}/bookmarks/', recipe_data_payload, format='json')
        self.assertEqual(get_bookmark_response.status_code, status.HTTP_200_OK)

    def test_delete_a_bookmark(self):
        """Test Delete a bookmark /api/user/profile/:userid/bookmarks/"""
        user_logged_in_data = self.login_functionality()
        userID = user_logged_in_data['id']
        access_token = user_logged_in_data['tokens']['access']

        recipe_response_data = self.create_recipe_functionality(access_token).data

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        recipe_data_payload = {
            "id": recipe_response_data['id']
        }
        self.client.post(f'/api/user/profile/{userID}/bookmarks/', recipe_data_payload, format='json')

        delete_bookmark_response = self.client.delete(f'/api/user/profile/{userID}/bookmarks/', recipe_data_payload, format='json')
        self.assertEqual(delete_bookmark_response.status_code, status.HTTP_200_OK)

    def test_schema(self):
        """API Test schema"""
        schema_response = self.client.get('/api/schema/')
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)

    def test_get_user(self):
        """Test get user details"""
        access_token = self.login_functionality()['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        user_response = self.client.get('/api/user/')
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)

    def test_edit_user_detail_put(self):
        """Test edit user details (PUT)"""
        access_token = self.login_functionality()['tokens']['access']
        user_data = {
            "username":'testuserupdated',
            "email":'testuser@example.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        user_response = self.client.put('/api/user/', user_data, format='json')
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)

        """Test edit details when user_data entered wrongly"""
        incorrect_user_data = {
            "email":'testuser@example.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        second_user_response = self.client.put('/api/user/', incorrect_user_data, format='json')
        self.assertEqual(second_user_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_user_detail_patch(self):
        """Test edit user details (PATCH)"""
        access_token = self.login_functionality()['tokens']['access']
        user_data = {
            "email":'testuserupdated@example.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        user_response = self.client.patch('/api/user/', user_data, format='json')
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)

        """Test edit user details API when invalid mail sent"""
        invalid_mail = {
            "email":'abcdef',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        second_user_response = self.client.patch('/api/user/', invalid_mail, format='json')
        self.assertEqual(second_user_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset(self):
        """Test password reset"""
        user_data = {
            "email": "testuser@example.com"
        }
        user_response = self.client.post('/api/user/password/reset/', user_data, format='json')
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)

        user_data_not_present = {
            "email": "fakeuser@example.com"
        }
        second_user_response = self.client.post('/api/user/password/reset/', user_data_not_present, format='json')
        self.assertEqual(second_user_response.status_code, status.HTTP_400_BAD_REQUEST)
