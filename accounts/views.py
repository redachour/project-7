from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from PIL import Image

from . import forms


def sign_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    return redirect('accounts:profile')
                else:
                    messages.error(request, "User account has been disabled.")
            else:
                messages.error(request, "Username or password is incorrect.")
    return render(request, 'accounts/sign_in.html', {'form': form})


def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(
                request,
                "You're now a user! You've been signed in, too.")
            return redirect('accounts:profile')
    return render(request, 'accounts/sign_up.html', {'form': form})


def sign_out(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return redirect('home')


@login_required
def profile(request):
    ''' display profile informations '''
    profile = request.user.profile
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    '''edit user profile with a link to edit the image as well'''
    form = forms.ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, request.FILES or None,
                                 instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            if request.FILES:
                image = str(request.user.profile.avatar.file)
                resize = Image.open(image)
                # Resize image
                resize.thumbnail((300, 400), Image.ANTIALIAS)
                resize.save(image)
            return redirect('accounts:profile')
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def password_change(request):
    ''' view to change the password with more secure one'''
    form = forms.PasswordChangeForm()
    user = request.user
    if request.method == 'POST':
        form = forms.PasswordChangeForm(data=request.POST, user=user)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was changed!')
            return redirect('home')
    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def avatar_edit(request):
    ''' edit the image uploaded using javascript'''
    form = forms.CropForm()
    profile = request.user.profile
    if request.method == 'POST':
        form = forms.CropForm(request.POST)
        if form.is_valid():
            image = str(profile.avatar.file)
            edit = Image.open(image)
            scale = float(form.cleaned_data['scale'])
            angle = 0 - float(form.cleaned_data['angle'])
            x = float(form.cleaned_data['x'])
            y = float(form.cleaned_data['y'])
            w = float(form.cleaned_data['w'])
            h = float(form.cleaned_data['h'])
            coordinates = (x/scale, y/scale, (x + w)/scale, (y + h)/scale)
            if angle != 0:
                edit = edit.rotate(angle, expand=True)
            edit = edit.crop(coordinates)
            edit.save(image)
            return redirect('accounts:profile')
    return render(request, 'accounts/avatar_edit.html',
                  {'profile': profile, 'form': form})
