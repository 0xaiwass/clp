from datetime import timedelta
from django.utils import timezone
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from .forms import *
from .models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import *
#------------------------------------------------------------------
class LoginView(View):

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next') or reverse('home:home')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        form = UserLoginForm()
        return render(request, 'accounts/login.html', context={'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(phone=phone)
                if not user.is_active:
                    messages.error(request, 'اطلاعات داده شده نادرست است. لطفا دویاره امتحان کنید', extra_tags='error')
                    return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'اطلاعات داده شده نادرست است. لطفا دویاره امتحان کنید', extra_tags='error')
                return redirect('accounts:login')
            user = authenticate(request, phone=phone, password=password)
            if user is not None:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                login(request, user)
                request.session.set_expiry(3600)
                messages.success(request, 'با موفقیت وارد شدید!', extra_tags='success')
                return redirect(self.next)
            else:
                messages.error(request, 'اطلاعات داده شده نادرست است. لطفا دوباره امتحان کنید', extra_tags='error')
                return redirect('accounts:login')
        messages.error(request, 'دوباره امتحان کنید', extra_tags='primary')
        return redirect('accounts:login')
#------------------------------------------------------------------
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect('home:home')
#------------------------------------------------------------------
class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home:home')
        form = UserRegisterForm()
        return render(request, 'accounts/register.html', context={'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password1']

            if not request.session.session_key:
                request.session.create()

            request.session['UserRegisterInfo'] = {
                'phone': phone,
                'password': password
            }
            request.session['verify_purpose'] = 'register'

            try:
                otp = str(random.randint(100000, 999999))
                request.session['otp'] = otp
                OTPCode.objects.create(
                    phone=phone,
                    session_key=request.session.session_key,
                    code=hashlib.sha256(otp.encode()).hexdigest(),
                    created_at=timezone.now(),
                )
                send_otp_code(phone, otp)
                messages.success(request, 'کد یکبارمصرف ارسال شد', extra_tags='success')
                return redirect('accounts:verify')
            except Exception as e:
                print(e)
                messages.error(request, 'خطا در ارسال کد. لطفا دوباره امتحان کنید.', extra_tags='error')
                # Clear session data on error
                request.session.pop('UserRegisterInfo', None)
                request.session.pop('verify_purpose', None)
        return render(request, 'accounts/register.html', context={'form': form})
#------------------------------------------------------------------
class ResetPasswordView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home:home')
        return render(request, 'accounts/reset-password.html', {'form': forms.ResetPasswordForm()})

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']

            # Step 1: Check if user exists
            if not User.objects.filter(phone=phone).exists():
                messages.error(request, 'کاربری با این شماره پیدا نشد.', extra_tags='error')
                return render(request, 'accounts/reset-password.html', {'form': form})

            # Step 2: Create session key if missing
            if not request.session.session_key:
                request.session.create()

            # Step 3: Store verification purpose & phone
            request.session['verify_purpose'] = 'reset'
            request.session['reset_phone'] = phone

            # Step 4: generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp  # optional, for debugging

            # Step 5: Save hashed OTP in DB
            OTPCode.objects.create(
                phone=phone,
                session_key=request.session.session_key,
                code=hashlib.sha256(otp.encode()).hexdigest(),
                created_at=timezone.now(),
            )

            # Step 6: Send OTP via SMS
            try:
                send_otp_code(phone, otp)  # send plain numeric OTP
                messages.success(request, 'کد یکبارمصرف ارسال شد.', extra_tags='success')
                return redirect('accounts:verify')
            except Exception as e:
                print("OTP ERROR:", e)
                messages.error(request, 'خطا در ارسال کد. لطفا دوباره امتحان کنید.', extra_tags='error')
                # Clear session data on error
                request.session.pop('verify_purpose', None)
                request.session.pop('reset_phone', None)

        return render(request, 'accounts/reset-password.html', {'form': form})
#------------------------------------------------------------------
class NewPasswordView(View):
    template_name = "accounts/new-password.html"

    def get(self, request):
        if not request.session.get("OTPVerified"):
            messages.error(request, "ابتدا باید کد تایید را وارد کنید.", extra_tags="error")
            return redirect("accounts:resetpassword")
        return render(request, self.template_name, {'form': forms.NewPasswordForm()})

    def post(self, request):
        if not request.session.get("OTPVerified"):  # lowercase & consistent
            messages.error(request, "ابتدا باید کد تایید را وارد کنید.", extra_tags="error")
            return redirect("accounts:resetpassword")

        form = NewPasswordForm(request.POST)
        if not form.is_valid():
            # The form will already have error messages for invalid data
            return render(request, self.template_name, {'form': form})

        phone = request.session.get("reset_phone")
        if not phone:
            messages.error(request, "خطا در بازیابی اطلاعات جلسه.", extra_tags="error")
            return redirect("accounts:resetpassword")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            messages.error(request, "خطا در بازیابی اطلاعات کاربر.", extra_tags="error")
            return redirect("accounts:resetpassword")

        # Set new password
        user.set_password(form.cleaned_data['password1'])
        user.save()

        # Clear session keys after successful password change
        self._clear_reset_session(request)

        messages.success(request, "رمز عبور با موفقیت تغییر کرد.", extra_tags="success")
        return redirect("accounts:login")

    def _clear_reset_session(self, request):
        for key in ["OTPVerified", "reset_phone", "verify_purpose"]:
            request.session.pop(key, None)
#------------------------------------------------------------------
class VerifyCodeView(View):
    def get(self, request):
        if not request.session.get('verify_purpose'):
            raise Http404()
        return render(request, 'accounts/verify.html', {'form': VerifyForm()})

    def post(self, request):
        if not request.session.get('verify_purpose'):
            raise Http404()

        purpose = request.session['verify_purpose']

        # Get phone based on purpose
        if purpose == 'register':
            user_info = request.session.get('UserRegisterInfo')
            if not user_info:
                messages.error(request, 'خطا در بازیابی اطلاعات.', extra_tags='error')
                return redirect('accounts:register')
            phone = user_info['phone']
        elif purpose == 'reset':
            phone = request.session.get('reset_phone')
            if not phone:
                messages.error(request, 'خطا در بازیابی اطلاعات.', extra_tags='error')
                return redirect('accounts:resetpassword')
        else:
            raise Http404()

        # Fetch latest OTP
        code_instance = OTPCode.objects.filter(
            phone=phone,
            session_key=request.session.session_key
        ).order_by('-id').first()

        if not code_instance:
            messages.error(request, 'رمز یکبار مصرف پیدا نشد', extra_tags='error')
            return self._redirect_on_error(purpose)

        # Check expiry (1 minute as requested)
        if timezone.now() - code_instance.created_at > timedelta(minutes=1):
            code_instance.delete()
            messages.error(request, 'رمز یکبارمصرف منقضی شده است.', extra_tags='error')
            return self._redirect_on_error(purpose)

        form = VerifyForm(request.POST)
        if form.is_valid():
            submitted_hash = hashlib.sha256(form.cleaned_data['code'].encode()).hexdigest()
            if submitted_hash == code_instance.code:
                code_instance.delete()

                if purpose == 'register':
                    return self._handle_registration_success(request)
                elif purpose == 'reset':
                    return self._handle_reset_success(request)
            else:
                messages.error(request, 'کد نامعتبر است.', extra_tags='error')
        else:
            messages.error(request, 'فرم ارسال شده نامعتبر است.', extra_tags='error')

        # If form is invalid or code is wrong, render with errors
        return render(request, 'accounts/verify.html', {'form': form})

    def _handle_registration_success(self, request):
        """Handle successful registration verification"""
        try:
            data = request.session['UserRegisterInfo']
            user = User.objects.create_user(
                phone=data['phone'],
                password=data['password']
            )
            user.is_active = True  # <-- activate user after OTP verification
            user.save()
            self._clear_session(request)
            messages.success(request, 'ثبت نام موفقیت آمیز بود', extra_tags='success')
            return redirect('accounts:login')
        except Exception:
            messages.error(request, 'خطا در ثبت نام. لطفا دوباره امتحان کنید.', extra_tags='error')
            return redirect('accounts:register')

    def _handle_reset_success(self, request):
        """Handle successful reset verification"""
        request.session['OTPVerified'] = True
        messages.success(request, 'لطفا رمز عبور جدید خود را وارد کنید.', extra_tags='success')
        return redirect('accounts:newpassword')

    def _redirect_on_error(self, purpose):
        """Redirect to appropriate page based on purpose"""
        return redirect('accounts:resetpassword' if purpose == 'reset' else 'accounts:register')

    def _clear_session(self, request):
        """Clear all session keys"""
        for key in ['UserRegisterInfo', 'verify_purpose', 'reset_phone', 'OTPVerified']:
            request.session.pop(key, None)
#------------------------------------------------------------------
class DashboardView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request, public_id):
        user = get_object_or_404(User, public_id=public_id)

        # Prevent IDOR → only allow owner or superuser
        if not request.user.is_superuser and request.user != user:
            return redirect('accounts:dashboard', public_id=request.user.public_id)

        addresses = Address.objects.filter(user=user)

        return render(request, 'accounts/dashboard.html', context={'user': user, 'addresses': addresses})
#------------------------------------------------------------------
#------------------------------------------------------------------
class ProfileAddressView(LoginRequiredMixin, View):
    template_name = "accounts/address.html"

    def get(self, request):
        addresses = request.user.addresses.all().order_by("-created_at")
        form = AddressForm()
        return render(request, self.template_name, {
            "addresses": addresses,
            "form": form
        })
#------------------------------------------------------------------
class AddAddressView(LoginRequiredMixin, View):
    template_name = "accounts/add_address.html"

    def get(self, request):
        form = AddressForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "آدرس با موفقیت اضافه شد.")
            return redirect("accounts:profile_address")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return render(request, self.template_name, {"form": form})
#------------------------------------------------------------------
class UpdateAddressView(LoginRequiredMixin, View):
    template_name = "accounts/address_edit.html"

    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        form = AddressForm(instance=address)
        return render(request, self.template_name, {"form": form, "address": address})

    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "آدرس با موفقیت بروزرسانی شد.")
            return redirect("accounts:profile_address")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return render(request, self.template_name, {"form": form, "address": address})
# ------------------------------------------------------------------
class DeleteAddressView(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        try:
            address.delete()
            messages.success(request, "آدرس با موفقیت حذف شد.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("accounts:profile_address")
#------------------------------------------------------------------
#------------------------------------------------------------------
class ProfileWishlistView(View):
    def get(self, request):
        return render(request, 'accounts/whishlist.html')

    def post(self, request):
        pass
#------------------------------------------------------------------
