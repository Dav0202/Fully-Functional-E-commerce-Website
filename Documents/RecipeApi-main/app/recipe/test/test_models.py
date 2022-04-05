from django.test import TestCase
from django.contrib.auth import get_user_model 
from .. import models

def sample_user(email= 'test@email.com',password = '43322'):
    """create sample user"""
    return get_user_model().objects.create_user(email,password)

class ModelTest(TestCase):

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Vegan'
        )
        self.assertEqual(str(tag),tag.name)