import datetime
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Feedback, GatePass, RequestBox, Room, UserProfile, CustomUser, AdminSecurity
from .forms import CustomUserCreationForm, LoginForm, ProfileForm
from django.contrib import messages
from django.utils import timezone 
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback
from datetime import date
from textblob import TextBlob  
from django.shortcuts import render, redirect
from .models import UserRoom, Vacancy, Room
from hostel.models import Vacancy
from .models import UserRoom
from .forms import RoomDetailsForm
from django.http import JsonResponse

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'hostelite'  # Set default role as hostelite
            user.save()
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'GET':
        # Clear any existing messages when loading the login page
        storage = messages.get_messages(request)
        storage.used = True
        return render(request, 'login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        security_key = request.POST.get('security_key')
        
        # Check if trying to login as admin
        if user_type == 'admin':
            if username == 'admin12345' and password == 'admin@12345':
                try:
                    admin_security = AdminSecurity.objects.first()
                    if admin_security and security_key == admin_security.security_key:
                        # Get or create admin user
                        admin_user, created = CustomUser.objects.get_or_create(
                            username='admin12345',
                            defaults={
                                'role': 'admin',
                                'is_staff': True,
                                'is_superuser': True
                            }
                        )
                        
                        # Update admin user permissions
                        admin_user.is_staff = True
                        admin_user.is_superuser = True
                        admin_user.role = 'admin'
                        
                        if created:
                            admin_user.set_password('admin@12345')
                            admin_user.save()
                        
                        # Authenticate and login
                        admin_user = authenticate(request, username='admin12345', password='admin@12345')
                        if admin_user:
                            login(request, admin_user)
                            return redirect('admin_dashboard')
                        else:
                            messages.error(request, 'Admin authentication failed.')
                    else:
                        messages.error(request, 'Invalid security key for admin login.')
                except AdminSecurity.DoesNotExist:
                    messages.error(request, 'Admin security configuration not found.')
            else:
                messages.error(request, 'Invalid admin credentials.')
        else:
            # Regular user login
            user = authenticate(request, username=username, password=password)
            if user:
                if user.username == 'admin12345':
                    messages.error(request, 'Please use the admin login form with security key.')
                else:
                    login(request, user)
                    # Check if user has completed profile and room setup
                    try:
                        profile = UserProfile.objects.get(user=user)
                        room = UserRoom.objects.get(user=user)
                        user.profile_completed = True
                        user.save()
                        return redirect('user_dashboard')
                    except (UserProfile.DoesNotExist, UserRoom.DoesNotExist):
                        # If either profile or room is not set up, redirect to profile setup
                        return redirect('profile_setup')
            else:
                messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard view
@login_required
def user_dashboard(request):
    if not request.user.profile_completed:
        return redirect('profile_setup')
    return render(request, 'user_dashboard.html')

@login_required
def user_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    try:
        user_room = UserRoom.objects.get(user=request.user)
    except UserRoom.DoesNotExist:
        user_room = None

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'user_room': user_room,
    })

# Feedback view
@login_required
def feedback_view(request):
    return render(request, 'feedback_selection.html')

@login_required
def requestbox_view(request):
    if request.method == "POST":
        request_text = request.POST.get("request_text")
        RequestBox.objects.create(user=request.user, request_text=request_text, date_submitted=timezone.now())
        return redirect("user_dashboard")

    return render(request, "requestbox.html")

@login_required
def view_requests(request):
    user_requests = RequestBox.objects.filter(user=request.user).order_by("-date_submitted")
    return render(request, "view_requests.html", {"requests": user_requests})

# Vacancy view
@login_required
def vacancy_view(request):
    return render(request, 'vacancy.html')

@login_required
def gatepass_view(request):
    if request.method == "POST":
        reason = request.POST.get("reason")
        departure_date = request.POST.get("departure_date")
        return_date = request.POST.get("return_date")
        departure_time = request.POST.get("departure_time")
        return_time = request.POST.get("return_time")

        # Convert string inputs to datetime objects
        departure_datetime = timezone.make_aware(
            timezone.datetime.combine(
                timezone.datetime.strptime(departure_date, "%Y-%m-%d").date(),
                timezone.datetime.strptime(departure_time, "%H:%M").time()
            )
        )
        return_datetime = timezone.make_aware(
            timezone.datetime.combine(
                timezone.datetime.strptime(return_date, "%Y-%m-%d").date(),
                timezone.datetime.strptime(return_time, "%H:%M").time()
            )
        )

        # Determine if the GatePass should be active
        now = timezone.localtime(timezone.now())
        status = departure_datetime <= now <= return_datetime

        # Save the data
        GatePass.objects.create(
            user=request.user,
            date_of_issue=timezone.now(),
            reason=reason,
            departure_date=departure_date,
            return_date=return_date,
            departure_time=departure_time,
            return_time=return_time,
            status=status,  # Set status dynamically
        )

        return redirect("user_dashboard")

    return render(request, "gatepass.html")

@login_required
def view_gatepasses(request):
    gatepasses = GatePass.objects.filter(user=request.user).order_by("-date_of_issue")  # Show latest first
    return render(request, "view_gatepasses.html", {"gatepasses": gatepasses})

@login_required
def feedback_selection(request):
    """Renders the meal selection page."""
    return render(request, "feedback_selection.html")

@login_required
def feedback_form(request):
    """Renders the feedback form based on the selected meal."""
    meal_type = request.GET.get("meal", "Lunch")  # Default to Lunch if no meal is provided
    return render(request, "feedback_form.html", {"meal_type": meal_type})

@login_required
def view_past_feedbacks(request):
    user_feedbacks = Feedback.objects.filter(user=request.user).order_by('-date')
    
    # Convert the date to the correct format
    for feedback in user_feedbacks:
        feedback.formatted_date = feedback.date.strftime("%d %b %Y")
    
    context = {
        'user_feedbacks': user_feedbacks
    }
    return render(request, 'view_past_feedbacks.html', context)

@login_required
def feedback_form(request):
    """Renders the feedback form based on the selected meal."""
    meal_type = request.GET.get("meal", "Lunch")  # Default to Lunch if no meal is provided
    return render(request, "feedback_form.html", {"meal_type": meal_type})

def submit_feedback(request):
    if request.method == "POST":
        meal_type = request.POST.get("meal_type")  # "Breakfast", "Lunch", or "Dinner"
        rating = request.POST.get("rating")

        # Get or create today's feedback entry
        feedback, created = Feedback.objects.get_or_create(user=request.user, date=date.today())

        # Check if feedback for the specific meal type has already been given
        if getattr(feedback, f"{meal_type.lower()}_rating"):  
            messages.error(request, f"You have already submitted feedback for {meal_type} today.")
            return redirect("feedback_selection")  # Redirect back to the feedback selection page

        # Save the feedback for the specific meal type
        setattr(feedback, f"{meal_type.lower()}_rating", rating)
        feedback.save()

        messages.success(request, f"Feedback for {meal_type} submitted successfully!")
        return redirect("feedback_selection")

    return redirect("feedback_selection")


@login_required
def profile_setup(request):
    # Check if the user has already completed profile and room setup
    try:
        profile = UserProfile.objects.get(user=request.user)
        room = UserRoom.objects.get(user=request.user)
        # If both exist, user has completed setup
        request.user.profile_completed = True
        request.user.save()
        return redirect('user_dashboard')
    except (UserProfile.DoesNotExist, UserRoom.DoesNotExist):
        # Continue with profile setup if not complete
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == "POST":
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('room_details')
        else:
            form = ProfileForm(instance=profile)

        return render(request, 'profile_setup.html', {'form': form})

@login_required
def room_details(request):
    # Check if user already has a room assigned
    try:
        room_assignment = UserRoom.objects.get(user=request.user)
        # If room exists, mark profile as complete and redirect to dashboard
        request.user.profile_completed = True
        request.user.save()
        return redirect('user_dashboard')
    except UserRoom.DoesNotExist:
        room_assignment = None

    if request.method == "POST":
        form = RoomDetailsForm(request.POST, instance=room_assignment)
        if form.is_valid():
            user_room = form.save(commit=False)
            user_room.user = request.user
            user_room.save()
            # Set profile completion flag
            request.user.profile_completed = True
            request.user.save()
            return redirect('user_dashboard')
    else:
        form = RoomDetailsForm(instance=room_assignment)

    return render(request, 'room_details.html', {'form': form})


def vacancy_list(request):
    # Get all vacancies
    vacancies = Vacancy.objects.all().order_by('room_number', 'bed_number')
    
    # Get all occupied rooms (rooms that have at least one bed occupied)
    occupied_rooms = set(UserRoom.objects.values_list('room__room_number', flat=True))
    
    # Get all room numbers that have at least one vacancy
    available_rooms = set(Vacancy.objects.values_list('room_number', flat=True))
    
    return render(request, 'vacancy.html', {
        'vacancies': vacancies,
        'occupied_rooms': list(occupied_rooms),
        'available_rooms': list(available_rooms),
    })


@login_required
def select_vacancy(request):
    if request.method == "POST":
        user = request.user
        room_number = request.POST.get("room_number")
        bed_number = request.POST.get("bed_number")

        # Get the user's current room (if exists)
        try:
            user_room = UserRoom.objects.get(user=user)
            # Move the old room and bed to the vacancy list
            Vacancy.objects.create(room_number=user_room.room.room_number, bed_number=user_room.bed_no)
        except UserRoom.DoesNotExist:
            user_room = None

        # Remove the newly selected room and bed from the vacancy list
        Vacancy.objects.filter(room_number=room_number, bed_number=bed_number).delete()

        # Assign the new room to the user
        selected_room = Room.objects.get(room_number=room_number)

        if user_room:
            # Update existing UserRoom entry
            user_room.room = selected_room
            user_room.bed_no = bed_number
            user_room.save()
        else:
            # Create a new UserRoom entry if not assigned before
            UserRoom.objects.create(user=user, room=selected_room, bed_no=bed_number)

        return redirect(reverse("vacancy_list")) # Redirect back to vacancy page

    return redirect("home")


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check for specific admin credentials
        if request.user.username != 'admin12345' or not request.user.is_staff or not request.user.is_superuser:
            return redirect('user_dashboard')  # Silently redirect without error message
            
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_dashboard(request):
    # Additional security check
    if request.user.username != 'admin12345':
        messages.error(request, 'Access denied. Only the admin can access this page.')
        return redirect('user_dashboard')
    return render(request, 'admin_dashboard.html')

@login_required
@admin_required
def feedback_analysis(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'feedback_analysis.html', {'feedbacks': feedbacks})

@login_required
@admin_required
def view_all_requests(request):
    requests = RequestBox.objects.all()
    return render(request, 'admin_view_requests.html', {'requests': requests})

@login_required
@admin_required
def view_all_vacancies(request):
    # Get all rooms
    rooms = Room.objects.all().order_by('room_number')
    
    # Get all user room assignments
    user_rooms = {(room.room.room_number, room.bed_no): room.user 
                 for room in UserRoom.objects.select_related('room', 'user')}
    
    # Prepare room data
    room_data = []
    for room in rooms:
        beds = []
        for bed in ['A', 'B', 'C']:  # Each room has 3 beds
            user = user_rooms.get((room.room_number, bed))
            beds.append({
                'bed_number': bed,
                'user': user.username if user else None
            })
        room_data.append({
            'room_number': room.room_number,
            'beds': beds
        })
    
    return render(request, 'admin_view_vacancies.html', {'room_data': room_data})

@login_required
@admin_required
def view_all_gatepasses(request):
    gatepasses = GatePass.objects.all()
    return render(request, 'admin_view_gatepasses.html', {'gatepasses': gatepasses})

@login_required
@admin_required
def manage_users(request):
    user_profiles = UserProfile.objects.select_related('user').all()
    user_rooms = {user_room.user_id: user_room for user_room in UserRoom.objects.select_related('room').all()}
    
    # Combine profile and room data
    for profile in user_profiles:
        profile.room_info = user_rooms.get(profile.user_id)
    
    return render(request, 'manage_users.html', {'user_profiles': user_profiles})


def analyze_sentiment(feedback_text):
    """AI-powered sentiment analysis using TextBlob."""
    if not feedback_text.strip():  # Handle empty strings
        return 0  # Neutral sentiment for empty feedback
    analysis = TextBlob(feedback_text)
    return analysis.sentiment.polarity  # Returns sentiment score (-1 to 1)

def feedback_analysis(request):
    today = now().date()  # Get today's date

    # Rating categories (assuming ratings range from 1 to 5)
    rating_scale = [1, 2, 3, 4, 5]

    # Collect rating counts for each meal
    breakfast_ratings = {rate: Feedback.objects.filter(date=today, breakfast_rating=rate).count() for rate in rating_scale}
    lunch_ratings = {rate: Feedback.objects.filter(date=today, lunch_rating=rate).count() for rate in rating_scale}
    dinner_ratings = {rate: Feedback.objects.filter(date=today, dinner_rating=rate).count() for rate in rating_scale}

    # Perform sentiment analysis on today's feedback
    feedback_entries = Feedback.objects.filter(date=today)
    sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}

    for feedback in feedback_entries:
        text = []

        # Ensure only non-null values are added
        if feedback.breakfast_rating is not None:
            text.append(f"Breakfast: {feedback.breakfast_rating}")
        if feedback.lunch_rating is not None:
            text.append(f"Lunch: {feedback.lunch_rating}")
        if feedback.dinner_rating is not None:
            text.append(f"Dinner: {feedback.dinner_rating}")

        text = " ".join(text)  # Create a full sentence from ratings
        sentiment_score = analyze_sentiment(text)

        # Categorizing Sentiment
        if sentiment_score > 0.2:
            sentiments['positive'] += 1
        elif sentiment_score < -0.2:
            sentiments['negative'] += 1
        else:
            sentiments['neutral'] += 1

    # Convert data to JSON for frontend
    data_json = json.dumps({
        'breakfast': breakfast_ratings,
        'lunch': lunch_ratings,
        'dinner': dinner_ratings,
        'sentiments': sentiments  # Include AI-analyzed sentiment counts
    })

    # Debugging: Print JSON in server logs
    print("Today's Feedback JSON:", data_json)

    context = {
        'data_json': data_json  # Pass JSON to template
    }

    return render(request, 'feedback_analysis.html', context)


def get_available_beds(request):
    room_id = request.GET.get('room_id')
    
    if room_id:
        all_beds = ['A', 'B', 'C']
        occupied_beds = list(UserRoom.objects.filter(room_id=room_id).values_list('bed_no', flat=True))
        available_beds = [bed for bed in all_beds if bed not in occupied_beds]

        return JsonResponse({'available_beds': available_beds})
    
    return JsonResponse({'available_beds': []})

def welcome(request):
    return render(request, 'welcome.html')








