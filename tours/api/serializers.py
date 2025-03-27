from rest_framework import serializers
from django.contrib.auth.models import User
from tours.models import Destination, Hotel, Attraction, Review, Excursion, Booking, Guide, Favorite

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class ReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'hotel', 'attraction', 'destination', 'author', 'author_name', 'rating', 'comment', 'created_at', 'approved']
        read_only_fields = ['id', 'created_at']
    
    def get_author_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return obj.author

class DestinationSerializer(serializers.ModelSerializer):
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'description', 'country', 'city', 'image', 'cover_image',
            'climate', 'vacation_type', 'featured', 'latitude', 'longitude',
            'created_at', 'updated_at', 'reviews_count', 'average_rating'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_reviews_count(self, obj):
        return obj.reviews.filter(approved=True).count()
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(approved=True)
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / reviews.count()

class HotelSerializer(serializers.ModelSerializer):
    destination_name = serializers.ReadOnlyField(source='destination.name')
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'destination', 'destination_name', 'price_per_night', 
            'rating', 'image', 'cover_image', 'gallery_images', 'description',
            'address', 'accommodation_type', 'amenities', 'latitude', 
            'longitude', 'booking_url', 'created_at', 'updated_at', 'reviews_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_reviews_count(self, obj):
        return obj.reviews.filter(approved=True).count()

class AttractionSerializer(serializers.ModelSerializer):
    destination_name = serializers.ReadOnlyField(source='destination.name')
    
    class Meta:
        model = Attraction
        fields = [
            'id', 'name', 'destination', 'destination_name', 'description',
            'latitude', 'longitude', 'image', 'cover_image', 'attraction_type',
            'price', 'opening_hours', 'website', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ExcursionSerializer(serializers.ModelSerializer):
    destination_name = serializers.ReadOnlyField(source='destination.name')
    included_attractions_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'name', 'destination', 'destination_name', 'description',
            'price', 'duration', 'excursion_type', 'image', 'cover_image',
            'gallery_images', 'included_attractions', 'included_attractions_details',
            'meeting_point', 'booking_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_included_attractions_details(self, obj):
        attractions = obj.included_attractions.all()
        return AttractionSerializer(attractions, many=True, context=self.context).data

class BookingSerializer(serializers.ModelSerializer):
    hotel_name = serializers.ReadOnlyField(source='hotel.name', default=None)
    excursion_name = serializers.ReadOnlyField(source='excursion.name', default=None)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_name', 'hotel', 'hotel_name', 'excursion', 'excursion_name',
            'check_in_date', 'check_out_date', 'excursion_date', 'adults',
            'children', 'total_price', 'status', 'booking_reference',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'booking_reference']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

class GuideSerializer(serializers.ModelSerializer):
    destination_name = serializers.ReadOnlyField(source='destination.name')
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Guide
        fields = [
            'id', 'title', 'user', 'user_name', 'destination', 'destination_name',
            'content', 'pdf_file', 'attractions', 'created_at', 'is_public'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        if not obj.user:
            return None
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

class FavoriteSerializer(serializers.ModelSerializer):
    destination_details = serializers.SerializerMethodField()
    hotel_details = serializers.SerializerMethodField()
    attraction_details = serializers.SerializerMethodField()
    excursion_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'destination', 'destination_details',
            'hotel', 'hotel_details', 'attraction', 'attraction_details',
            'excursion', 'excursion_details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_destination_details(self, obj):
        if not obj.destination:
            return None
        return DestinationSerializer(obj.destination, context=self.context).data
    
    def get_hotel_details(self, obj):
        if not obj.hotel:
            return None
        return HotelSerializer(obj.hotel, context=self.context).data
    
    def get_attraction_details(self, obj):
        if not obj.attraction:
            return None
        return AttractionSerializer(obj.attraction, context=self.context).data
    
    def get_excursion_details(self, obj):
        if not obj.excursion:
            return None
        return ExcursionSerializer(obj.excursion, context=self.context).data 