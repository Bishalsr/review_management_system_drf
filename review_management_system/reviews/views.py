from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import Review, ReviewImage, HelpfulVote, BusinessResponse
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewImageUploadSerializer,
    HelpfulVoteSerializer, BusinessResponseCreateSerializer
)

# Public APIs
class ReviewListAPIView(generics.ListAPIView):
    queryset = Review.objects.filter(status='approved')
    serializer_class = ReviewSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'comment', 'customer_name']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        rating = self.request.query_params.get('rating')
        verified = self.request.query_params.get('verified_purchase')
        if product_id:
            qs = qs.filter(product_id=product_id)
        if rating:
            qs = qs.filter(rating__gte=rating)
        if verified in ['true', 'false']:
            qs = qs.filter(is_verified_purchase=(verified=='true'))
        return qs

class ReviewCreateAPIView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer

    def perform_create(self, serializer):
        serializer.save(status='pending')

class ReviewDetailAPIView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# Image Upload
class ReviewImageUploadAPIView(generics.CreateAPIView):
    serializer_class = ReviewImageUploadSerializer

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        if review.images.count() >= 5:
            return Response({"error": "Maximum 5 images allowed"}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(review=review)
        return Response(serializer.data)

# Helpful Vote
class ReviewVoteAPIView(generics.CreateAPIView):
    serializer_class = HelpfulVoteSerializer

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        data = request.data
        voter_email = data.get('voter_email')
        if voter_email == review.customer_email:
            return Response({"error": "Cannot vote on your own review"}, status=400)
        vote, created = HelpfulVote.objects.update_or_create(
            review=review, voter_email=voter_email,
            defaults={'is_helpful': data.get('is_helpful', True)}
        )
        return Response({
            "helpful_count": review.helpful_count(),
            "not_helpful_count": review.not_helpful_count()
        })

# List all pending reviews
@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_reviews(request):
    reviews = Review.objects.filter(status='pending')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# Moderate review (approve/reject)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def moderate_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    status_choice = request.data.get('status')
    if status_choice not in ['approved', 'rejected']:
        return Response({"error": "Invalid status"}, status=400)
    review.status = status_choice
    review.save()
    serializer = ReviewSerializer(review)
    return Response(serializer.data)


# Add business response
@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_response(request, pk):
    review = get_object_or_404(Review, pk=pk, status='approved')
    if hasattr(review, 'businessresponse'):
        return Response({"error": "Response already exists"}, status=400)
    
    serializer = BusinessResponseCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(review=review)
    return Response(serializer.data)


# Soft delete review
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def soft_delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.status = 'rejected'
    review.save()
    return Response({"message": "Review soft deleted"})


@api_view(['GET'])
def review_stats(request):
   product_id = request.query_params.get('product_id')
   if not product_id:
       return Response({"error":"product_d is required"},status=400)
   
   reviews = Review.objects.filter(product_id=product_id,status='approved')
   total_reviews = reviews.count()
   
   
   average_rating = reviews.aggregate(Avg('rating'))
   
   if average_rating is None:
       average_rating = 0
       
   rating_distribution = {
       "5":reviews.filter(rating=5).count(),
       "4":reviews.filter(rating=4).count(),
       "3":reviews.filter(rating=3).count(),
       "2":reviews.filter(rating=2).count(),
       "1":reviews.filter(rating=1).count()
   } 
   
   
   verified_purchase_count=reviews.filter(is_verified_purchase=True).count()
   
   with_images_count = 0
   for review in reviews:
       if review.has_images():
           with_images_count += 1
           
   with_response_count = 0   
   for review in reviews:
       if review.has_response():
           with_response_count += 1
               
   
   return Response(
       {
           "product_id":int(product_id),
           "total_reviews":total_reviews,
           "average_rating":average_rating,
           "rating_distribution":rating_distribution,
           "verified_purchase_count":verified_purchase_count,
           "with_images_count":with_images_count,
           "with_response_count":with_response_count
           
           
       }
   )