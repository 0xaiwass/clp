from django.http import Http404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
#----------------------------------------------------------------------------------------------------
class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Block entire admin prefix for non-superusers (incl. unauth)
        if request.path.startswith('/spr-82hxQv/') and not request.user.is_superuser:
            raise Http404("Page not found.")

        response = self.get_response(request)
        return response
#----------------------------------------------------------------------------------------------------
class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check authenticated users
        if request.user.is_authenticated:
            # Get session expiry age (in seconds); if >3600s idle, logout
            expiry_age = request.session.get_expiry_age()
            if expiry_age is not None and expiry_age <= 0:  # Expired
                logout(request)  # Clear session
                # Redirect to login with expired flag
                messages.info(request, 'جلسه شما به دلیل عدم فعالیت منقضی شد. لطفا دوباره وارد شوید.', extra_tags='warning')
                return redirect(reverse('accounts:login'))

            # Reset expiry on activity (slides window to now +1h)
            request.session.set_expiry(3600)

        response = self.get_response(request)
        return response
#----------------------------------------------------------------------------------------------------
