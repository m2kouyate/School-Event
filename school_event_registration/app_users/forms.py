from django import forms
from django.contrib.auth.models import User
from .models import Profile


class ProfileRegistrationForm(forms.ModelForm):
    about = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'cols': 30, 'rows': 5})
    )
    class Meta:
        model = Profile
        fields = ['profile_picture', 'about']
        required = {
            'about': False
        }


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['profile_picture', 'about', 'username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("First name can only contain letters")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise forms.ValidationError("Last name can only contain letters")
        return last_name


class ProfileDeleteForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = []


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password (e.g., SecureP@ss123)'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'placeholder': 'Repeat Password'}))
    username = forms.CharField(
        max_length=150,
        help_text='',
        widget=forms.TextInput(attrs={'placeholder': 'Username (e.g., johndoe123)'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'First Name (e.g., John)'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name (e.g., Doe)'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email (e.g., johndoe@example.com)'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email



