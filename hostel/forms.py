from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, GatePass, UserProfile, UserRoom, Room
from hostel import models
from django.db.models import Count

class CustomUserCreationForm(UserCreationForm):
	class Meta:
            model = CustomUser
            fields = ['username', 'password1', 'password2']
          

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        disabled=True,
        required=False,
        widget=forms.HiddenInput()
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),  # Date picker in HTML
        required=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'user', 'name', 'guardian_name', 'student_mobile', 
            'guardian_mobile', 'residential_address', 'education', 'dob', 
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['user'].initial = self.instance.user
            self.fields['user'].queryset = CustomUser.objects.filter(id=self.instance.user.id)

    def clean_student_mobile(self):
        student_mobile = self.cleaned_data.get('student_mobile')
        if not student_mobile.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(student_mobile) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits long.")
        if student_mobile[0] == '0':
            raise forms.ValidationError("Mobile number cannot start with 0.")
        return student_mobile

    def clean_guardian_mobile(self):
        guardian_mobile = self.cleaned_data.get('guardian_mobile')
        if not guardian_mobile.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(guardian_mobile) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits long.")
        if guardian_mobile[0] == '0':
            raise forms.ValidationError("Mobile number cannot start with 0.")
        return guardian_mobile

class RoomDetailsForm(forms.ModelForm):
    class Meta:
        model = UserRoom
        fields = ['room', 'bed_no']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Step 1: Fetch rooms that have less than 3 users assigned
        occupied_rooms = UserRoom.objects.values('room').annotate(user_count=Count('room')).filter(user_count__lt=3)
        available_room_ids = [entry['room'] for entry in occupied_rooms]

        # Step 2: Include completely empty rooms
        empty_rooms = Room.objects.filter(userroom__isnull=True)

        # Step 3: Combine both querysets
        self.fields['room'].queryset = Room.objects.filter(
            id__in=[*available_room_ids, *empty_rooms.values_list('id', flat=True)]
        )

        # Step 4: Set available bed choices dynamically
        self.fields['bed_no'].choices = self.get_available_beds()

        # Help texts
        self.fields['room'].help_text = "Select an available room."
        self.fields['bed_no'].help_text = "Select an available bed (A, B, or C)."

    def get_available_beds(self):
        """
        Get available beds for the selected room.
        """
        all_beds = ['A', 'B', 'C']  # All possible beds

        # Get currently selected room (if exists)
        selected_room = self.initial.get('room')

        if selected_room:
            occupied_beds = list(UserRoom.objects.filter(room=selected_room).values_list('bed_no', flat=True))
            available_beds = [(bed, bed) for bed in all_beds if bed not in occupied_beds]
        else:
            available_beds = [(bed, bed) for bed in all_beds]  # Default all beds if no room is selected yet

        return available_beds if available_beds else [('', 'No beds available')]  # Prevent empty dropdown

class GatePassForm(forms.ModelForm):
    class Meta:
        model = GatePass
        fields = ['reason', 'departure_date', 'return_date', 'departure_time', 'return_time']
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'return_time': forms.TimeInput(attrs={'type': 'time'}),
        }