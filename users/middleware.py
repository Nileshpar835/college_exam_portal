from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

class AccessDeniedMiddleware:
    """
    Middleware to handle unauthorized access attempts and redirect to access_denied page.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if this is a redirect to login with next parameter
        if (response.status_code == 302 and 
            response.url and 
            '/accounts/login/?next=' in response.url):
            
            # Extract the attempted URL
            next_url = response.url.split('next=')[1] if 'next=' in response.url else ''
            
            # If user is not authenticated, redirect to access_denied
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to access that page.')
                return redirect('users:access_denied')
        
        return response

    def process_exception(self, request, exception):
        """
        Handle permission denied exceptions.
        """
        from django.core.exceptions import PermissionDenied
        
        if isinstance(exception, PermissionDenied):
            if request.user.is_authenticated:
                messages.error(request, 'You do not have permission to access this page.')
            else:
                messages.error(request, 'You must be logged in to access that page.')
            return redirect('users:access_denied')
        
        return None
