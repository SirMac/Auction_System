from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.messages import error
from django.db.utils import OperationalError
import logging


def handleDBConnectionError(func):
    def inner_function(req, *args, **kwargs):
        try:
            return func(req, *args, **kwargs)
        except OperationalError as e:
            logging.error(f'OperationalError: {e}')
            error(request=req, message='Database connection error')
            return redirect(req.path)
    return inner_function


def loggedIn(func):
    def inner_function(req, *args, **kwargs):
        if not req.user.is_authenticated:
            return func(req, *args, **kwargs)
        return redirect('contacts:index')
    return inner_function


def isUserRegistered(username):
    try:
        User.objects.get(username=username)
    except (KeyError, User.DoesNotExist):
       return False
    else:
       return True
    


def redirectPageNotFound(req, exception): 
    pass