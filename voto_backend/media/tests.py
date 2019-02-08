from django.test import TestCase
from content.models import Image
# Create your tests here.


class ImageTestCase(TestCase):
    def setUp(self):
        Image.objects.create(image='../../VotoTestBackend/media/tests/test.jpg',
                             name='Hello')
