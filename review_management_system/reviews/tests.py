from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Review, HelpfulVote

class ReviewModelTest(TestCase):
    def setUp(self):
        self.review = Review.objects.create(
            product_id=1, customer_email='test@example.com',
            customer_name='John Doe', rating=5, title='Great Product',
            comment='Loved it', status='approved'
        )

    def test_helpful_count(self):
        HelpfulVote.objects.create(review=self.review, voter_email='a@a.com', is_helpful=True)
        HelpfulVote.objects.create(review=self.review, voter_email='b@b.com', is_helpful=False)
        self.assertEqual(self.review.helpful_count(), 1)
        self.assertEqual(self.review.not_helpful_count(), 1)

    def test_has_images_response(self):
        self.assertFalse(self.review.has_images())
        self.assertFalse(self.review.has_response())


class ReviewAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.review_data = {
            "product_id": 1,
            "customer_email": "test2@example.com",
            "customer_name": "Alice",
            "rating": 4,
            "title": "Very Good",
            "comment": "Nice product"
        }

    def test_create_review(self):
        response = self.client.post('/api/reviews/', self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_review(self):
        self.client.post('/api/reviews/', self.review_data)
        response = self.client.post('/api/reviews/', self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews(self):
        self.client.post('/api/reviews/', self.review_data)
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, 200)
