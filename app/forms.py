
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MathForm(forms.Form):
    """ This form is placed on home page and  gets expression to calculate"""
    math = forms.CharField(label="Type your math expression", max_length=400, min_length=1,
                           # widget=forms.TextInput(attrs={'size': 50, "class": "col-xs-3"})
                           widget=forms.TextInput(attrs={"class": "w-50 p-0 red"})
                           )


class NewUserForm(UserCreationForm):  # class NewUserForm(forms.ModelForm):
    """ obviously """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
