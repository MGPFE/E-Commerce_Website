from django import forms
from .models import User, Address


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")

    class Meta:
        # password = forms.CharField(widget=forms.PasswordInput)
        model = User
        fields = ["username", "email"]
        # widgets = {
        #     "password": forms.PasswordInput()
        # }
        help_texts = {
            "username": None
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Wpisz swój login'
        self.fields["email"].widget.attrs["placeholder"] = "Wpisz swój email"
        self.fields['password'].widget.attrs['placeholder'] = 'Wpisz hasło'


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")

    class Meta:
        model = User
        fields = ["username"]
        help_texts = {
            "username": None
        }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Wpisz swój login'
        self.fields['password'].widget.attrs['placeholder'] = 'Wpisz hasło'


class EditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["address", "city", "zipcode"]


class ConfirmPaymentForm(forms.Form):
    file = forms.FileField(label="Załącz plik (.pdf lub zdjęcie)")


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, label="Kod weryfikacyjny")

    def __init__(self, *args, **kwargs):
        super(VerifyForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['placeholder'] = 'Wpisz swój kod weryfikacyjny'


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Potwierdź hasło")

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['placeholder'] = 'Wprowadź nowe hasło'
        self.fields['confirm_password'].widget.attrs['placeholder'] = 'Potwierdź nowe hasło'


class ResetPasswordEmailForm(forms.Form):
    mail = forms.EmailField(max_length=50, label="Email")

    def __init__(self, *args, **kwargs):
        super(ResetPasswordEmailForm, self).__init__(*args, **kwargs)
        self.fields['mail'].widget.attrs['placeholder'] = 'Podaj adres email swojego konta'
