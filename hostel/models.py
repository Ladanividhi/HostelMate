from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone 
from django.contrib.auth.models import User
from textblob import TextBlob

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    profile_completed = models.BooleanField(default=False)
   

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hostelite', 'Hostelite'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='hostelite')

    
def __str__(self):
    	return f"{self.username} ({self.role})"

class AdminSecurity(models.Model):
    security_key = models.CharField(max_length=100, default='secretpassword')
    is_configured = models.BooleanField(default=False)

    def __str__(self):
        return "Admin Security Configuration"

# User Profile Model
class UserProfile(models.Model):
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
	name = models.CharField(max_length=100)
	guardian_name = models.CharField(max_length=100)
	student_mobile = models.CharField(max_length=15)
	guardian_mobile = models.CharField(max_length=15)
	residential_address = models.TextField()
	education = models.CharField(max_length=100)
	dob = models.DateField(null=True,blank=True)

	def __str__(self):
            return self.name

# User Room Model
class Room(models.Model):
    room_number = models.IntegerField(unique=True)  # Unique room number
    capacity = models.IntegerField(default=3)  # Max 3 users per room

    def __str__(self):
        return f"Room {self.room_number}"

class UserRoom(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)  
    bed_no = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Remove from Vacancy when a room is assigned
        Vacancy.objects.filter(room_number=self.room.room_number, bed_number=self.bed_no).delete()

    def delete(self, *args, **kwargs):
        # Re-add to Vacancy when a user leaves a room
        Vacancy.objects.create(room_number=self.room.room_number, bed_number=self.bed_no)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Room {self.room.room_number} - Bed {self.bed_no}"


class GatePass(models.Model):
    gatepass_id = models.AutoField(primary_key=True)  # Explicitly define the primary key

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_of_issue = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    departure_date = models.DateField()
    return_date = models.DateField()
    departure_time = models.TimeField()
    return_time = models.TimeField()
    status = models.BooleanField(default=True)  # Default to Active

    def is_active(self):
        """
        Determines whether the GatePass is still active.
        It is active if the current date and time is within departure and return range.
        """
        now = timezone.localtime(timezone.now())

        # Combine departure and return dates with their respective times
        departure_datetime = timezone.make_aware(
            timezone.datetime.combine(self.departure_date, self.departure_time)
        )
        return_datetime = timezone.make_aware(
            timezone.datetime.combine(self.return_date, self.return_time)
        )

        # Check if current datetime is within the range
        return departure_datetime <= now <= return_datetime


# Vacancy Model
class Vacancy(models.Model):
	room_number = models.CharField(max_length=10)
	bed_number = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])

	def __str__(self):
    	    return f"Room {self.room_number} - Bed {self.bed_number}"

# Request Box Model
class RequestBox(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request_text = models.TextField(default=" ")  # User can write their request
    date_submitted = models.DateField(default=timezone.now)  # Auto-set today's date

    def __str__(self):
        return f"Request by {self.user.username} on {self.date_submitted}"

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    breakfast_rating = models.IntegerField(null=True, blank=True)
    lunch_rating = models.IntegerField(null=True, blank=True)
    dinner_rating = models.IntegerField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    
    # New sentiment fields
    breakfast_sentiment = models.CharField(max_length=10, null=True, blank=True)
    lunch_sentiment = models.CharField(max_length=10, null=True, blank=True)
    dinner_sentiment = models.CharField(max_length=10, null=True, blank=True)
    overall_sentiment = models.CharField(max_length=10, null=True, blank=True)

    def analyze_sentiment(self, text):
        """AI-powered sentiment analysis using TextBlob."""
        analysis = TextBlob(text)
        sentiment_score = analysis.sentiment.polarity  # Ranges from -1 to 1
        return sentiment_score

    def save(self, *args, **kwargs):
        """Calculate sentiment before saving."""
        text = []
        if self.breakfast_rating is not None:
            text.append(f"Breakfast: {self.breakfast_rating}")
        if self.lunch_rating is not None:
            text.append(f"Lunch: {self.lunch_rating}")
        if self.dinner_rating is not None:
            text.append(f"Dinner: {self.dinner_rating}")
        
        full_text = " ".join(text)
        sentiment_score = self.analyze_sentiment(full_text)

        # Categorizing Sentiment
        if sentiment_score > 0.2:
            self.overall_sentiment = "positive"
        elif sentiment_score < -0.2:
            self.overall_sentiment = "negative"
        else:
            self.overall_sentiment = "neutral"

        super().save(*args, **kwargs)  # Save model

    def __str__(self):
        return f"Feedback by {self.user.username} on {self.date}"
