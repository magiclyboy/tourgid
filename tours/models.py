from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Destination(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='destinations/covers/', null=True, blank=True, help_text="Large hero image for the destination page")
    climate = models.CharField(max_length=100, blank=True)
    vacation_type = models.CharField(max_length=100, blank=True)
    featured = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    ACCOMMODATION_TYPES = [
        ('hotel', 'Hotel'),
        ('hostel', 'Hostel'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('resort', 'Resort'),
    ]
    
    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    image = models.ImageField(upload_to='hotels/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='hotels/covers/', null=True, blank=True, help_text="Large hero image for the hotel detail page")
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of image URLs for the hotel gallery")
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    accommodation_type = models.CharField(max_length=20, choices=ACCOMMODATION_TYPES, default='hotel')
    amenities = models.JSONField(default=dict, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    booking_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Attraction(models.Model):
    ATTRACTION_TYPES = [
        ('cultural', 'Cultural'),
        ('nature', 'Nature'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('food', 'Food & Dining'),
        ('sports', 'Sports & Activities'),
    ]
    
    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='attractions')
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='attractions/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='attractions/covers/', null=True, blank=True, help_text="Large hero image for the attraction page")
    attraction_type = models.CharField(max_length=20, choices=ATTRACTION_TYPES, default='cultural')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    author = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    
    def __str__(self):
        reviewed_item = self.hotel or self.attraction or self.destination
        return f"Review by {self.author} for {reviewed_item.name if reviewed_item else 'unknown'}"

class Excursion(models.Model):
    EXCURSION_TYPES = [
        ('cultural', 'Cultural'),
        ('adventure', 'Adventure'),
        ('shopping', 'Shopping'),
        ('food', 'Food & Culinary'),
        ('nature', 'Nature'),
        ('historical', 'Historical'),
    ]
    
    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='excursions')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100)  # e.g., "3 hours", "Full day"
    excursion_type = models.CharField(max_length=20, choices=EXCURSION_TYPES, default='cultural')
    image = models.ImageField(upload_to='excursions/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='excursions/covers/', null=True, blank=True, help_text="Large hero image for the excursion page")
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of image URLs for the excursion gallery")
    included_attractions = models.ManyToManyField(Attraction, related_name='excursions', blank=True)
    meeting_point = models.CharField(max_length=255, blank=True)
    booking_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    excursion_date = models.DateTimeField(null=True, blank=True)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.hotel:
            return f"Hotel booking for {self.hotel.name} by {self.user.username}"
        else:
            return f"Excursion booking for {self.excursion.name} by {self.user.username}"

class Guide(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guides', null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='guides')
    content = models.TextField()
    pdf_file = models.FileField(upload_to='guides/', null=True, blank=True)
    attractions = models.ManyToManyField(Attraction, related_name='guides', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Guide for {self.destination.name}: {self.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.destination:
            return f"{self.user.username}'s favorite: {self.destination.name}"
        elif self.hotel:
            return f"{self.user.username}'s favorite: {self.hotel.name}"
        elif self.attraction:
            return f"{self.user.username}'s favorite: {self.attraction.name}"
        elif self.excursion:
            return f"{self.user.username}'s favorite: {self.excursion.name}"
        return f"{self.user.username}'s favorite"
