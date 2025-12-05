from django.http import Http404
from django.urls import resolve

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check for authenticated users and custom admin paths
        if (request.user.is_authenticated and request.path.startswith('/spr-82hxQv/')):
            # Resolve the URL to confirm it's admin-related
            try:
                match = resolve(request.path)
                if match.app_name == 'admin' and not request.user.is_superuser:
                    raise Http404("Page not found.")
            except:
                pass  # Not an admin URL or resolution failed, proceed

        response = self.get_response(request)
        return response
