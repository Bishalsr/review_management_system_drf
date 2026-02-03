from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator

class Review(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    product_id = models.IntegerField()
    customer_email = models.EmailField(validators=[EmailValidator()])
    customer_name = models.CharField(max_length=100)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField(blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product_id', 'customer_email')
        ordering = ['-created_at']

    def helpful_count(self):
        return self.helpfulvote_set.filter(is_helpful=True).count()

    def not_helpful_count(self):
        return self.helpfulvote_set.filter(is_helpful=False).count()

    def has_images(self):
        return self.images.exists()

    def has_response(self):
        return hasattr(self, 'businessresponse')
    
    

    def __str__(self):
        return f"{self.customer_name} - {self.title}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review,related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='review_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class BusinessResponse(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    response_text = models.TextField()
    responder_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class HelpfulVote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    voter_email = models.EmailField()
    is_helpful = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'voter_email')
