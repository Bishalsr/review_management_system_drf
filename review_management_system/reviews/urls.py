from django.urls import path
from .views import (
    ReviewListAPIView, ReviewCreateAPIView, ReviewDetailAPIView,
    ReviewImageUploadAPIView, ReviewVoteAPIView,
    pending_reviews, moderate_review, add_response, soft_delete_review,
    review_stats
)

urlpatterns = [
    # Public endpoints
    path('reviews/', ReviewListAPIView.as_view()),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view()),
    path('reviews/', ReviewCreateAPIView.as_view()),
    path('reviews/<int:pk>/images/', ReviewImageUploadAPIView.as_view()),
    path('reviews/<int:pk>/vote/', ReviewVoteAPIView.as_view()),
    path('reviews/stats/', review_stats),

    # Admin endpoints
    path('admin/reviews/pending/', pending_reviews),
    path('admin/reviews/<int:pk>/moderate/', moderate_review),
    path('admin/reviews/<int:pk>/respond/', add_response),
    path('admin/reviews/<int:pk>/', soft_delete_review),
]
