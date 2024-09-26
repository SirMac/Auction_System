from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.messages import error
from .userValidators import ValidateUser
import logging
from .utils import loggedIn, handleDBConnectionError, isUserRegistered



@loggedIn
def loginUser(req):
    if req.method == 'GET':
        return render(req, 'accounts/login.html')
    
    return authenticateUser(req)
    

@handleDBConnectionError
def authenticateUser(req):
    username = req.POST['username']
    password = req.POST['password']

    if not isUserRegistered(username):
        message = f'Username ({username}) not found'
        logging.error(message)
        error(request=req, message=message)
        return redirect('users:login') 

    user = authenticate(request=req, username=username, password=password)

    if user is None:
        message = 'Invalid password'
        logging.error(message)
        error(request=req, message=message)
        return redirect('users:login')
    
    login(req, user)
    return redirect('auctions:index')


@loggedIn
def registerUser(req):
    if req.method  == 'GET':
        return render(req, 'accounts/register.html')
    
    return createUser(req)



@handleDBConnectionError
def createUser(req):
    username = req.POST['username']
    email = req.POST['email']
    password1 = req.POST['password1']

    if isUserRegistered(username):
        message = f'User ({username}) already exists'
        logging.warning(message)
        error(request=req, message=message)
        return redirect('users:register')

    validateUser = ValidateUser(req.POST)
    messages = validateUser.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
            error(request=req, message=message)
        return redirect('users:register')

    user = User(username=username, email=email, password=password1)
    user.save()
    user.set_password(user.password)
    user.save()
    return redirect('users:login')
    
    
        
        


def logoutUser(req):
    logout(req)
    return redirect('users:login')



    