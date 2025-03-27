from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg
import logging
import requests
import json
import random
from .models import Booking, Hotel, Destination, Guide, Attraction

logger = logging.getLogger(__name__)

@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Send booking confirmation email to the user
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        if booking.hotel:
            subject = f"Your booking at {booking.hotel.name} is confirmed!"
            template = 'emails/hotel_booking_confirmation.html'
            context = {
                'booking': booking,
                'hotel': booking.hotel,
                'user': booking.user,
            }
        else:
            subject = f"Your excursion booking for {booking.excursion.name} is confirmed!"
            template = 'emails/excursion_booking_confirmation.html'
            context = {
                'booking': booking,
                'excursion': booking.excursion,
                'user': booking.user,
            }
        
        html_message = render_to_string(template, context)
        
        send_mail(
            subject=subject,
            message='',  # Plain text version (not used)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent for booking {booking_id}")
        return f"Booking confirmation email sent for booking {booking_id}"
    
    except Booking.DoesNotExist:
        logger.error(f"Booking with ID {booking_id} not found")
        return f"Error: Booking with ID {booking_id} not found"
    
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {str(e)}")
        return f"Error sending booking confirmation email: {str(e)}"

@shared_task
def update_hotel_ratings():
    """
    Update hotel ratings based on user reviews
    """
    try:
        hotels = Hotel.objects.all()
        updated_count = 0
        
        for hotel in hotels:
            avg_rating = hotel.reviews.filter(approved=True).aggregate(Avg('rating'))['rating__avg']
            
            if avg_rating is not None:
                hotel.rating = round(avg_rating, 1)
                hotel.save(update_fields=['rating'])
                updated_count += 1
        
        logger.info(f"Updated ratings for {updated_count} hotels")
        return f"Updated ratings for {updated_count} hotels"
    
    except Exception as e:
        logger.error(f"Error updating hotel ratings: {str(e)}")
        return f"Error updating hotel ratings: {str(e)}"

@shared_task
def generate_city_guide(destination_id):
    """
    Generate a city guide for a destination
    """
    try:
        destination = Destination.objects.get(id=destination_id)
        attractions = Attraction.objects.filter(destination=destination)
        
        if not attractions:
            logger.error(f"No attractions found for destination {destination_id}")
            return f"Error: No attractions found for destination {destination_id}"
        
        # Generate a simple guide
        guide_title = f"Complete Guide to {destination.name}, {destination.country}"
        
        guide_content = f"""
# {guide_title}

## Overview
{destination.description}

## Weather & Climate
{destination.climate or 'Information not available'}

## Top Attractions
"""
        
        # Add top attractions
        for i, attraction in enumerate(attractions[:10], 1):
            guide_content += f"""
### {i}. {attraction.name}
* **Type:** {attraction.get_attraction_type_display()}
* **Price:** {"Free" if not attraction.price or attraction.price == 0 else f"${attraction.price}"}
* **Opening Hours:** {attraction.opening_hours or 'Information not available'}

{attraction.description}
"""
        
        # Create the guide
        guide = Guide.objects.create(
            title=guide_title,
            destination=destination,
            content=guide_content,
            is_public=True
        )
        
        # Add the attractions to the guide
        guide.attractions.set(attractions[:10])
        
        logger.info(f"City guide generated for {destination.name}")
        return f"City guide generated for {destination.name}, guide ID: {guide.id}"
    
    except Destination.DoesNotExist:
        logger.error(f"Destination with ID {destination_id} not found")
        return f"Error: Destination with ID {destination_id} not found"
    
    except Exception as e:
        logger.error(f"Error generating city guide: {str(e)}")
        return f"Error generating city guide: {str(e)}"

@shared_task
def check_booking_status():
    """
    Check and update booking status
    """
    try:
        # Get all pending bookings older than 24 hours
        yesterday = timezone.now() - timezone.timedelta(hours=24)
        pending_bookings = Booking.objects.filter(status='pending', created_at__lt=yesterday)
        
        updated_count = 0
        for booking in pending_bookings:
            # Simulate API call to external booking system
            # In a real scenario, you'd check with a real payment provider or booking system
            status_options = ['confirmed', 'cancelled']
            new_status = random.choice(status_options)
            
            booking.status = new_status
            booking.save(update_fields=['status'])
            updated_count += 1
            
            # If confirmed, send email
            if new_status == 'confirmed':
                send_booking_confirmation_email.delay(booking.id)
        
        logger.info(f"Updated status for {updated_count} bookings")
        return f"Updated status for {updated_count} bookings"
    
    except Exception as e:
        logger.error(f"Error checking booking status: {str(e)}")
        return f"Error checking booking status: {str(e)}"

@shared_task
def get_weather_data(destination_id):
    """
    Get weather data for a destination from an external API
    """
    try:
        destination = Destination.objects.get(id=destination_id)
        
        if not destination.latitude or not destination.longitude:
            logger.error(f"Destination with ID {destination_id} doesn't have coordinates")
            return f"Error: Destination with ID {destination_id} doesn't have coordinates"
        
        # For demo purposes - would use a real API in production
        # This is mocked data
        weather_data = {
            'destination_id': destination_id,
            'destination_name': destination.name,
            'current_temp': random.randint(5, 35),
            'weather_condition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Snowy']),
            'humidity': random.randint(30, 90),
            'wind_speed': random.randint(0, 30),
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Weather data fetched for {destination.name}")
        return weather_data
    
    except Destination.DoesNotExist:
        logger.error(f"Destination with ID {destination_id} not found")
        return f"Error: Destination with ID {destination_id} not found"
    
    except Exception as e:
        logger.error(f"Error getting weather data: {str(e)}")
        return f"Error getting weather data: {str(e)}"

@shared_task
def generate_weekly_featured_guides():
    """
    Generate city guides for all featured destinations
    that don't have guides yet
    """
    try:
        featured_destinations = Destination.objects.filter(featured=True)
        guides_created = 0
        
        for destination in featured_destinations:
            # Check if a guide already exists
            if Guide.objects.filter(destination=destination).exists():
                continue
            
            # Generate the guide
            result = generate_city_guide(destination.id)
            if not result.startswith("Error"):
                guides_created += 1
        
        logger.info(f"Created {guides_created} new featured guides")
        return f"Created {guides_created} new featured guides"
    
    except Exception as e:
        logger.error(f"Error generating weekly featured guides: {str(e)}")
        return f"Error generating weekly featured guides: {str(e)}" 