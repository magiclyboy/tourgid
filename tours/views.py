from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg, Q, Count
from .models import Destination, Hotel, Attraction, Excursion, Review, Guide, Favorite
from django.db import models

def home(request):
    featured_destinations = Destination.objects.filter(featured=True)[:6]
    top_hotels = Hotel.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:4]
    popular_excursions = Excursion.objects.order_by('-created_at')[:4]
    
    context = {
        'featured_destinations': featured_destinations,
        'top_hotels': top_hotels,
        'popular_excursions': popular_excursions,
    }
    return render(request, 'tourgid/home.html', context)

def destinations(request):
    # Get filter parameters from request
    country = request.GET.get('country', '')
    climate = request.GET.get('climate', '')
    vacation_type = request.GET.get('vacation_type', '')
    
    # Start with all destinations
    destinations_list = Destination.objects.all()
    
    # Apply filters if provided
    if country:
        destinations_list = destinations_list.filter(country__icontains=country)
    if climate:
        destinations_list = destinations_list.filter(climate__icontains=climate)
    if vacation_type:
        destinations_list = destinations_list.filter(vacation_type__icontains=vacation_type)
    
    # Pagination
    paginator = Paginator(destinations_list, 9)  # Show 9 destinations per page
    page = request.GET.get('page')
    destinations = paginator.get_page(page)
    
    # Get unique countries for filtering
    countries = Destination.objects.values_list('country', flat=True).distinct()
    
    context = {
        'destinations': destinations,
        'countries': countries,
        'selected_country': country,
        'selected_climate': climate,
        'selected_vacation_type': vacation_type,
    }
    return render(request, 'tourgid/destinations.html', context)

def destination_detail(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    hotels = destination.hotels.all()
    attractions = destination.attractions.all()
    excursions = destination.excursions.all()
    reviews = destination.reviews.filter(approved=True)
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'destination': destination,
        'hotels': hotels,
        'attractions': attractions,
        'excursions': excursions,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'tourgid/destination_detail.html', context)

def hotels(request):
    # Get filter parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    accommodation_type = request.GET.get('accommodation_type', '')
    destination = request.GET.get('destination', '')
    
    # Start with all hotels
    hotels_list = Hotel.objects.all()
    
    # Apply filters
    if min_price:
        hotels_list = hotels_list.filter(price_per_night__gte=min_price)
    if max_price:
        hotels_list = hotels_list.filter(price_per_night__lte=max_price)
    if rating:
        hotels_list = hotels_list.filter(rating__gte=rating)
    if accommodation_type:
        hotels_list = hotels_list.filter(accommodation_type=accommodation_type)
    if destination:
        hotels_list = hotels_list.filter(destination__name__icontains=destination)
    
    # Sorting
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'price_asc':
        hotels_list = hotels_list.order_by('price_per_night')
    elif sort_by == 'price_desc':
        hotels_list = hotels_list.order_by('-price_per_night')
    elif sort_by == 'rating':
        hotels_list = hotels_list.order_by('-rating')
    
    # Pagination
    paginator = Paginator(hotels_list, 9)
    page = request.GET.get('page')
    hotels = paginator.get_page(page)
    
    # Get all destinations for filtering
    destinations = Destination.objects.all()
    
    context = {
        'hotels': hotels,
        'destinations': destinations,
        'min_price': min_price,
        'max_price': max_price,
        'rating': rating,
        'accommodation_type': accommodation_type,
        'selected_destination': destination,
        'sort': sort_by,
        'accommodation_types': Hotel.ACCOMMODATION_TYPES,
    }
    return render(request, 'tourgid/hotels.html', context)

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    reviews = hotel.reviews.filter(approved=True)
    
    # Related hotels in the same destination
    related_hotels = Hotel.objects.filter(destination=hotel.destination).exclude(id=hotel.id)[:4]
    
    context = {
        'hotel': hotel,
        'reviews': reviews,
        'related_hotels': related_hotels,
    }
    return render(request, 'tourgid/hotel_detail.html', context)

def excursions(request):
    # Get filter parameters
    excursion_type = request.GET.get('excursion_type', '')
    destination = request.GET.get('destination', '')
    max_price = request.GET.get('max_price')
    
    # Start with all excursions
    excursions_list = Excursion.objects.all()
    
    # Apply filters
    if excursion_type:
        excursions_list = excursions_list.filter(excursion_type=excursion_type)
    if destination:
        excursions_list = excursions_list.filter(destination__name__icontains=destination)
    if max_price:
        excursions_list = excursions_list.filter(price__lte=max_price)
    
    # Pagination
    paginator = Paginator(excursions_list, 9)
    page = request.GET.get('page')
    excursions = paginator.get_page(page)
    
    # Get all destinations for filtering
    destinations = Destination.objects.all()
    
    context = {
        'excursions': excursions,
        'destinations': destinations,
        'excursion_types': Excursion.EXCURSION_TYPES,
        'selected_type': excursion_type,
        'selected_destination': destination,
        'max_price': max_price,
    }
    return render(request, 'tourgid/excursions.html', context)

def excursion_detail(request, excursion_id):
    excursion = get_object_or_404(Excursion, id=excursion_id)
    attractions = excursion.included_attractions.all()
    
    # Related excursions in the same destination
    related_excursions = Excursion.objects.filter(
        destination=excursion.destination
    ).exclude(id=excursion.id)[:4]
    
    context = {
        'excursion': excursion,
        'attractions': attractions,
        'related_excursions': related_excursions,
    }
    return render(request, 'tourgid/excursion_detail.html', context)

def about(request):
    return render(request, 'tourgid/about.html')

@login_required
def add_review(request, content_type, content_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if content_type == 'hotel':
            content_object = get_object_or_404(Hotel, id=content_id)
            review = Review(
                user=request.user,
                hotel=content_object,
                author=request.user.username,
                rating=rating,
                comment=comment
            )
        elif content_type == 'destination':
            content_object = get_object_or_404(Destination, id=content_id)
            review = Review(
                user=request.user,
                destination=content_object,
                author=request.user.username,
                rating=rating,
                comment=comment
            )
        elif content_type == 'attraction':
            content_object = get_object_or_404(Attraction, id=content_id)
            review = Review(
                user=request.user,
                attraction=content_object,
                author=request.user.username,
                rating=rating,
                comment=comment
            )
        
        review.save()
        
        # Redirect back to the detail page
        if content_type == 'hotel':
            return redirect('hotel_detail', hotel_id=content_id)
        elif content_type == 'destination':
            return redirect('destination_detail', destination_id=content_id)
        elif content_type == 'attraction':
            return redirect('attraction_detail', attraction_id=content_id)
    
    # If not POST or other error, redirect to home
    return redirect('home')

@login_required
def add_to_favorites(request, content_type, content_id):
    if request.method == 'POST':
        if content_type == 'destination':
            content_object = get_object_or_404(Destination, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                destination=content_object
            )
        elif content_type == 'hotel':
            content_object = get_object_or_404(Hotel, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                hotel=content_object
            )
        elif content_type == 'attraction':
            content_object = get_object_or_404(Attraction, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                attraction=content_object
            )
        elif content_type == 'excursion':
            content_object = get_object_or_404(Excursion, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                excursion=content_object
            )
        
        # Redirect back to the referring page
        next_url = request.POST.get('next', '/')
        return redirect(next_url)
    
    return redirect('home')

@login_required
def remove_from_favorites(request, favorite_id):
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    favorite.delete()
    next_url = request.POST.get('next', '/')
    return redirect(next_url)

@login_required
def user_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'tourgid/user_favorites.html', context)

@login_required
def generate_city_guide(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    attractions = destination.attractions.all()
    
    # Create a basic guide (in a real app, this would be more sophisticated)
    guide = Guide.objects.create(
        title=f"Guide to {destination.name}",
        user=request.user,
        destination=destination,
        content=f"Explore the beautiful {destination.name} with our curated guide.",
        is_public=False
    )
    
    # Add attractions to the guide
    for attraction in attractions:
        guide.attractions.add(attraction)
    
    # In a real app, you'd generate a PDF here
    
    return redirect('guide_detail', guide_id=guide.id)

@login_required
def guide_detail(request, guide_id):
    guide = get_object_or_404(Guide, id=guide_id)
    
    # Check if the user has permission to view this guide
    if not guide.is_public and guide.user != request.user:
        return redirect('home')
    
    context = {
        'guide': guide,
        'attractions': guide.attractions.all(),
    }
    return render(request, 'tourgid/guide_detail.html', context)

def attraction_detail(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    reviews = attraction.reviews.filter(approved=True)
    
    # Related attractions in the same destination
    related_attractions = Attraction.objects.filter(
        destination=attraction.destination
    ).exclude(id=attraction.id)[:4]
    
    context = {
        'attraction': attraction,
        'reviews': reviews,
        'related_attractions': related_attractions,
    }
    return render(request, 'tourgid/attraction_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    
    if query:
        destinations = Destination.objects.filter(
            Q(name__icontains=query) | Q(country__icontains=query) | Q(city__icontains=query)
        )
        
        hotels = Hotel.objects.filter(
            Q(name__icontains=query) | Q(destination__name__icontains=query)
        )
        
        attractions = Attraction.objects.filter(
            Q(name__icontains=query) | Q(destination__name__icontains=query)
        )
        
        excursions = Excursion.objects.filter(
            Q(name__icontains=query) | Q(destination__name__icontains=query)
        )
    else:
        destinations = Destination.objects.none()
        hotels = Hotel.objects.none()
        attractions = Attraction.objects.none()
        excursions = Excursion.objects.none()
    
    context = {
        'query': query,
        'destinations': destinations,
        'hotels': hotels,
        'attractions': attractions,
        'excursions': excursions,
    }
    
    return render(request, 'tourgid/search_results.html', context)

def attractions(request):
    """View function for listing all attractions."""
    attraction_list = Attraction.objects.all().order_by('-created_at')
    
    # Handle search and filtering
    query = request.GET.get('q', '')
    attraction_type = request.GET.get('type', '')
    
    if query:
        attraction_list = attraction_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(destination__name__icontains=query)
        )
    
    if attraction_type:
        attraction_list = attraction_list.filter(attraction_type=attraction_type)
    
    # Pagination
    paginator = Paginator(attraction_list, 12)  # Show 12 attractions per page
    page = request.GET.get('page')
    
    try:
        attractions = paginator.page(page)
    except PageNotAnInteger:
        attractions = paginator.page(1)
    except EmptyPage:
        attractions = paginator.page(paginator.num_pages)
    
    # Get attraction types for filter
    attraction_types = dict(Attraction.ATTRACTION_TYPES)
    
    # Get popular destinations (featured or with most attractions)
    popular_destinations = Destination.objects.filter(featured=True)[:4]
    if popular_destinations.count() < 4:
        # Add more destinations if we don't have enough featured ones
        existing_ids = list(popular_destinations.values_list('id', flat=True))
        more_destinations = Destination.objects.exclude(id__in=existing_ids).annotate(
            attraction_count=models.Count('attractions')
        ).order_by('-attraction_count')[:4-popular_destinations.count()]
        popular_destinations = list(popular_destinations) + list(more_destinations)
    
    context = {
        'attractions': attractions,
        'query': query,
        'attraction_type': attraction_type,
        'attraction_types': attraction_types,
        'total_attractions': attraction_list.count(),
        'popular_destinations': popular_destinations,
    }
    
    return render(request, 'tourgid/attractions.html', context)

@login_required
def user_profile(request):
    """User profile view with bookings, favorites, and reviews"""
    user = request.user
    bookings = user.bookings.all().order_by('-created_at')[:5]
    favorites = user.favorites.all().order_by('-created_at')
    reviews = user.reviews.all().order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'bookings': bookings,
        'favorites': favorites,
        'reviews': reviews,
    }
    return render(request, 'tourgid/profile.html', context)

@login_required
def user_settings(request):
    """User settings view"""
    return render(request, 'tourgid/settings.html')

@login_required
def user_bookings(request):
    """User bookings view"""
    bookings = request.user.bookings.all().order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'tourgid/bookings.html', context)

def signup(request):
    """User registration view"""
    if request.method == 'POST':
        # Handle form submission
        # This is a simplified version - you'd typically use Django's UserCreationForm
        pass
    
    return render(request, 'tourgid/auth/signup.html')

