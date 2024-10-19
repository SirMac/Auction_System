from django.contrib.messages import error
from django.shortcuts import redirect
import logging


class ExceptionMiddleware:
    blackListPaths = ['/favicon.ico']
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        statusCode = response.status_code

        if statusCode == 500:
            logging.error(f"Server error (500) for {request.method} {request.path}")
            error(request=request, message='Somthing went wrong. Try again')
            return redirect(request.path)
        
        elif statusCode == 404 and request.path not in self.blackListPaths:
            logging.error(f"Page not found for {request.method} {request.path}")
            # if not request.user.is_authenticated:
            #     return redirect('users:login')
            return redirect('auctions:index')
        return response

