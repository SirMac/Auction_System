from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.messages import error, success
from .userValidators import ValidateUser, ValidateUserDeregistration
import logging
from .utils import loggedIn, handleDBConnectionError, isUserRegistered, isUerActive



@loggedIn
def loginUser(req):
    if req.method == 'GET':
        req.session['urlref'] = req.GET.get('next')
        return render(req, 'accounts/login.html')
    
    return authenticateUser(req)
    

@handleDBConnectionError
def authenticateUser(req):
    username = req.POST['username']
    password = req.POST['password']

    user = authenticate(request=req, username=username, password=password)

    if user is None or not isUerActive(username):
        message = 'Invalid username/password'
        logging.error(message)
        error(request=req, message=message)
        return redirect('users:login')
    
    login(req, user)
    urlReferer = req.session.get('urlref')
    if urlReferer:
        return redirect(urlReferer)
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
    firstName = req.POST['first_name']
    lastName = req.POST['last_name']
    

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

    user = User(username=username, email=email, password=password1, first_name=firstName, last_name=lastName)
    user.save()
    user.set_password(user.password)
    user.save()
    success(request=req, message='Registration successful. Provide credentials to login')
    return redirect('users:login')
    
    
        
def deregisterUser(req):
    username = req.user.username
    deregisterValidation = ValidateUserDeregistration(username)
    messages = deregisterValidation.errorMessages
    
    if messages:
        print('message-len:', len(messages))
        message = messages[len(messages)-1]
        # for message in messages:
        logging.error(message)
        error(request=req, message=message)
        return redirect('auctions:index')
    

    try:
        user = User.objects.get(username=username)
    except:
        logging.error('deregisterUser: Error occured when getting user')
        return redirect('auctions:index')
    else:
        user.is_active = 0
        user.save()
        logging.info(f"deregisterUser: User, '{username}' deregistered successfully")
        success(request=req, message=f"User, '{username}' have been deregistered successfully")
        return logoutUser(req)



def logoutUser(req):
    logout(req)
    return redirect('users:login')



    