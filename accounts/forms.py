from django import forms
from .models import *
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
import re   
#----------------------------------------------------------------------------------------
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تایید رمز عبور', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'phone')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("رمز عبور ها یکسان نیستند")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
#----------------------------------------------------------------------------------------
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label='password')

    class Meta:
        model = User
        fields = ('phone', 'email', 'password', 'last_login')

    def clean_password(self):
        return self.initial["password"]
#----------------------------------------------------------------------------------------
class UserLoginForm(forms.Form):
    phone = forms.CharField(max_length=11, required=True,
                            widget=forms.TextInput(attrs={'class': 'class="block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                                          'id':'username'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'class="block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                                                                   'type':'password',
                                                                                   'id':'passwd'}))
    class Meta:
        model = User
        fields = ('phone', 'password')
#----------------------------------------------------------------------------------------
def validate_password_strength(password):

    if len(password) < 8:
        raise ValidationError('رمز عبور باید حداقل ۸ کاراکتر باشد.')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('رمز عبور باید حداقل شامل یک حرف بزرگ باشد.')

    if not re.search(r'\d', password):
        raise ValidationError('رمز عبور باید حداقل شامل یک عدد باشد.')

    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        raise ValidationError('رمز عبور باید حداقل شامل یک کاراکتر ویژه باشد.')

class UserRegisterForm(forms.Form):
    phone = forms.CharField(max_length=11,
                            required=True,
                            widget=forms.TextInput(attrs={
                                'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                'type':'tel',
                                'id':'phone',
                                'name':'phone',
                                'placeholder': 'شماره تلفن خود را وارد کنید'}))
    password1 = forms.CharField(label='password',
                                required=True,
                                widget=forms.PasswordInput(attrs={
                                    'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                    'type':'password',
                                    'id':'password',
                                    'name':'password',
                                    'placeholder': 'رمز عبور خود را وارد کنید'}))
    password2 = forms.CharField(label='confirm',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                    'type':'password',
                                    'id':'rePassword',
                                    'name':'rePassword',
                                    'placeholder': 'رمز عبور خود را دوباره وارد کنید'}))

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)  # raises if invalid
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('رمز عبور و تکرار آن یکسان نمیباشد')
        return password2

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('کاربر گرامی شماره همراه نامعتبر می باشد لطفا دوباره امتحان کنید')
        return phone
#----------------------------------------------------------------------------------------
class VerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-3 outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',}),
    )

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError('کد ارسال شده صحیح نمیباشد.')
        return code
#----------------------------------------------------------------------------------------
class ResetPasswordForm(forms.Form):
    phone = forms.CharField(max_length=11,
                            required=True,
                            widget=forms.TextInput(attrs={
                                'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                'type':'tel',
                                'id':'phone',
                                'name':'phone',
                                'placeholder': 'شماره موبایل خود را وارد کنید'
                            }))
#----------------------------------------------------------------------------------------
class NewPasswordForm(forms.Form):
    password1 = forms.CharField(required=True,
                                widget=forms.PasswordInput(attrs={
                                    'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                    'type':'password',
                                    'placeholder': 'رمز عبور جدید خود را وارد کنید'
                                }))
    password2 = forms.CharField(required=True,
                                widget=forms.PasswordInput(attrs={
                                    'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                    'type':'password',
                                    'placeholder': 'رمز عبور جدید خود را دوباره وارد کنید',
                                }))

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            errors = validate_password_strength(password1)
            if errors:
                raise ValidationError(errors)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("رمز عبور و تکرار آن مطابقت ندارند.")

        return cleaned_data
#----------------------------------------------------------------------------------------
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "title",
            "province",
            "city",
            "street",
            "postal_code",
            "is_default",
        ]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                            "placeholder": "نام و نام‌خانوادگی به فارسی"}),
            "province": forms.TextInput(attrs={'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                               "placeholder": "استان تهران"}),
            "city": forms.TextInput(attrs={'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                           "placeholder": "شهرستان تهران"}),
            "street": forms.TextInput(attrs={'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                             "placeholder": "آدرس خیابان و کوی"}),
            "postal_code": forms.TextInput(attrs={'class': 'block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400',
                                                  "placeholder": "کدپستی ۱۰ رقمی"}),
            "is_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if postal_code and not postal_code.isdigit():
            raise forms.ValidationError("Postal code must contain only digits.")
        if postal_code and len(postal_code) != 10:
            raise forms.ValidationError("Postal code must be exactly 10 digits.")
        return postal_code
#----------------------------------------------------------------------------------------

