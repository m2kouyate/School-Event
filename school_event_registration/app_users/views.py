from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Profile
from .forms import ProfileRegistrationForm, ProfileUpdateForm, UserRegistrationForm


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('school_event_app:event_list')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileRegistrationForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            login(request, authenticate(username=new_user.username, password=user_form.cleaned_data['password']))
            return redirect('app_users:profile_detail', pk=new_user.profile.pk)
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileRegistrationForm()
    return render(request, 'users/register.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'users/profile_detail.html', {'profile': profile})


class ProfileUpdate(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'

    def form_valid(self, form):
        profile = form.save(commit=False)

        user = profile.user
        user.username = form.cleaned_data['username']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()

        profile.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_users:profile_detail', kwargs={'pk': self.object.pk})


class ProfileDelete(DeleteView):
    model = Profile
    template_name = 'users/profile_confirm_delete.html'
    success_url = reverse_lazy('school_event_app:event_list')






