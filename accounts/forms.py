import re

from django import forms
from . import models
from tinymce.widgets import TinyMCE


class ProfileForm(forms.ModelForm):
    email = forms.EmailField()
    confirm_email = forms.EmailField()
    date_of_birth = forms.DateField(input_formats=['%Y-%m-%d',
                                                   '%m/%d/%Y',
                                                   '%m/%d/%y'])
    bio = forms.CharField(widget=TinyMCE(attrs={'rows': 5}))
    avatar = forms.ImageField(required=False)

    class Meta:
        model = models.Profile
        fields = ['first_name',
                  'last_name',
                  'email',
                  'confirm_email',
                  'date_of_birth',
                  'bio',
                  'avatar',
                  'city',
                  'state',
                  'country',
                  'hobby']

    def clean_bio(self):
        bio = self.cleaned_data['bio']
        tags = re.compile('<.*?>')
        clean_bio = re.sub(tags, '', bio)
        if len(clean_bio) < 10:
            raise forms.ValidationError("Bio must be at least 10 characters.")
        return bio

    def clean_confirm_email(self):
        '''This checks to see if email and confirm_email match'''
        email = self.cleaned_data['email']
        confirm_email = self.cleaned_data['confirm_email']
        if email != confirm_email:
            raise forms.ValidationError("Emails must match")
        return confirm_email


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(required=True,
                                       widget=forms.PasswordInput())
    new_password = forms.CharField(required=True,
                                   widget=forms.PasswordInput(
                                    attrs={'data-indicator': 'pwindicator'}),
                                   min_length=14)
    confirm_password = forms.CharField(required=True,
                                       widget=forms.PasswordInput(),
                                       min_length=14)

    def __init__(self, data=None, user=None, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(data=data, *args, **kwargs)

    def clean(self):
        current_password = self.cleaned_data['current_password']
        new_password = self.cleaned_data['new_password']
        confirm_password = self.cleaned_data['confirm_password']

        if not self.user.check_password(current_password):
            raise forms.ValidationError('incorrect current password')

        if new_password == current_password:
            raise forms.ValidationError(
                "new password cannot be same as current password")

        pattern = ("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#*?&^$@!%])")
        regex = re.compile(pattern)
        if re.match(regex, new_password) is None:
            raise forms.ValidationError('''new password must contain upper
            and lowercase letters, numbers and characters from #*?&^$@!%.''')

        first = self.user.profile.first_name.lower()
        last = self.user.profile.last_name.lower()
        if ((first != '' and first in new_password.lower()) or
           (last != '' and last in new_password.lower()) or
           (self.user.username.lower() in new_password.lower())):
            raise forms.ValidationError(
                "password cannot contain your username, firstname or lastname")

        if new_password != confirm_password:
            raise forms.ValidationError("passwords don't match")


class CropForm(forms.Form):
    """ Hide fields to hold the coordinates chosen by the user """
    scale = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'display:none'}))
    angle = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'display:none'}))
    x = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    y = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    w = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    h = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
