from django.contrib import admin
from .models import Review, ReviewImage, BusinessResponse, HelpfulVote

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 5
    # readonly_fields = ['image']

class BusinessResponseInline(admin.StackedInline):
    model = BusinessResponse
    max_num = 1

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'customer_name', 'rating', 'status', 'created_at']
    list_filter = ['status', 'rating', 'is_verified_purchase', 'created_at']
    search_fields = ['customer_email', 'customer_name', 'title', 'comment']
    inlines = [ReviewImageInline, BusinessResponseInline]
    readonly_fields = ['customer_email', 'customer_name', 'product_id', 'rating']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(status='approved')
    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected')
    reject_reviews.short_description = "Reject selected reviews"
