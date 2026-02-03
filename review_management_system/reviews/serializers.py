from rest_framework import serializers
from .models import Review, ReviewImage, BusinessResponse, HelpfulVote

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'uploaded_at']

class BusinessResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessResponse
        fields = ['response_text', 'responder_name', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    business_response = BusinessResponseSerializer( read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField( read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product_id', 'customer_email', 'customer_name', 'rating',
            'title', 'comment', 'is_verified_purchase', 'status', 'created_at',
            'updated_at', 'images', 'business_response', 'helpful_count', 'not_helpful_count'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product_id', 'customer_email', 'customer_name', 'rating', 'title', 'comment']

    def validate_title(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Title must be at least 10 characters")
        return value

    def validate_comment(self, value):
        if value and len(value) > 2000:
            raise serializers.ValidationError("Comment max length 2000")
        return value

class ReviewImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['image']

class HelpfulVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpfulVote
        fields = ['voter_email', 'is_helpful']

class BusinessResponseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessResponse
        fields = ['response_text', 'responder_name']
