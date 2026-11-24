from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt
from . import models, forms
import os
import sys
import sqlite3
from datetime import datetime

#===========================================FLAWS & FIXES========================================
def auth_check(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You are not yet signed in.')
        raise PermissionDenied
def without_auth_check(request):
    return

def unauth_check(request): #check whether the request already contains authenticated user
    if request.user.is_authenticated:
        messages.error(request, 'You are already signed in. Sign out first to access the page')
        #print("user already authenticated, raising PermissionDenied")
        raise PermissionDenied
def without_unauth_check(request): #skip the authenticated user checking to enable resigning in/up without first signing out
    return

def hashed_sign_up(form): #use Django's built-in UserCreationForm to create users & save hashed passwords
    user = form.save(commit=False)
    user.save()
#A02:2021 – Cryptographic Failures & A07:2021 – Identification and Authentication Failures: Uses plain text, encrypted, or weakly hashed passwords data stores
#A03:2021 – Injection
#11111111'); DROP TABLE app_item --
def unhashed_sign_up(form): #manually save to the database with unhashed password 
    form.is_valid()
    data = form.cleaned_data
    print("unhashed sign up called with form's data",data)
    connection = sqlite3.connect('db.sqlite3')
    script = f"""
        INSERT INTO auth_user
            (
                last_login,
                is_superuser,
                first_name,
                last_name,
                email,
                is_staff,
                is_active,
                date_joined,
                username,
                password
            )
        VALUES 
            (
                NULL,
                0, 
                '', 
                '', 
                '', 
                0, 
                1, 
                '{datetime.now()}',
                '{data['username']}',
                '{data['password1']}')
        """
    #print("executing with script",script)
    connection.executescript(script),
    connection.close()
        
def hashed_sign_in(request,username,password): #use Django's built-in authenticator & login functions
    user = authenticate(request, username=username, password=password)
    if user is None:
        messages.error(request, 'Invalid username or password')
        form = forms.SignInForm()
        #print("user is",user,"rendering sign_in.html with form",form)
        return render(request, 'sign_in.html', {'form': form})
    login(request, user)
    messages.success(request, f'Welcome back, {user.username}.')
    #print("user is",user,"redirecting to front_page")
    return redirect('front_page')
#A07:2021 – Identification and Authentication Failures:
def unhashed_sign_in(request,username,password): #checking unhashed password by directly quering the User model
    #print("unhashed_sign_in called for request",request,"username",username,"password",password)
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        #print("user found, user is",user)
        if password == user.password:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}.')
            #print("password match, redirecting to front_page. user.is_authenticated is",user.is_authenticated)
            return redirect('front_page')
    except User.DoesNotExist:
        #print("user doesnt exist!")
        pass
    messages.error(request, 'Invalid username or password')
    form = forms.SignInForm()
    #print("rendering sign_in.html with form",form)
    return render(request, 'sign_in.html', {'form': form})


def loan_check(request, item_id): #returning the items if all checks are passed
    #print("loan_check requested for request",request,"request path",request.get_full_path(),"request's userid",request.user.id,"item_id",item_id)
    auth_check(request)
    item = models.Item.objects.get(id=item_id)
    #print("db query results in item",item)
    if item.item_loaner: #if it is already loaned, raise SuspiciousOperation
        #print("item is already loaned, raising error")
        raise SuspiciousOperation
    #print("loan_check passed, returning item")
    return item    
#A01:2021 – Broken Access Control: Violation of the principle of least privilege or deny by default, where access should only be granted for particular capabilities, roles, or users, but is available to anyone.
def without_loan_check(request, item_id): #skip the authenticated user checking to enable resigning in without first signing out
    return models.Item.objects.get(id=item_id)

def return_check(request, item_id): #returning the items if all checks are passed
    #print("return_check requested for request",request,"request path",request.get_full_path(),"request's userid",request.user.id,"item_id",item_id)
    auth_check(request)
    item = models.Item.objects.get(id=item_id)
    #print("db query results in item",item)
    if item.item_loaner == request.user: #if loaner_id != request.user.id, raise SuspiciousOperation
        #print("return_checks passed, returning item")
        return item
    #print("item is not loaned by the user, raising error")
    raise SuspiciousOperation
#A01:2021 – Broken Access Control: Violation of the principle of least privilege or deny by default, where access should only be granted for particular capabilities, roles, or users, but is available to anyone.
def without_return_check(request, item_id): #skip the authenticated user checking to enable resigning in without first signing out
    return models.Item.objects.get(id=item_id)

###########################################VIEWS##########################################

@csrf_exempt
def sign_in(request):
    try:
        #unauth_check(request)
        without_unauth_check(request)
    except PermissionDenied:
        return redirect('front_page')
    
    if request.method == 'GET':
        
        form = forms.SignInForm()
        #print("sign_in method GET called,request.GET data:",request.GET,"form.as_p",form.as_p)
        return render(request, 'sign_in.html', {'form': form})
    
    if request.method == 'POST':
        #print("sign in's CSRF token:",request.POST.get('csrfmiddlewaretoken'))
        form = forms.SignInForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            #return hashed_sign_in(request,username,password)
            return unhashed_sign_in(request,username,password)
        #print("form is invalid")
        messages.error(request, 'The provided credentials are invalid')
        return render(request, 'sign_in.html', {'form': form})

@csrf_exempt
def sign_up(request):
    try:
        #unauth_check(request)
        without_unauth_check(request)
    except PermissionDenied:
        return redirect('front_page')
    if request.method == 'POST':
        #form = forms.SignUpForm(request.POST)
        form = forms.CustomSignUpForm(request.POST) 
        #print("sign_up method POST called, the request data:",request,"request.POST data:",request.POST,"form data:",form)
        try:
            #hashed_sign_up(form)
            unhashed_sign_up(form)
        except ValueError:
            messages.error(request, 'The provided data are invalid')
            return redirect('sign_up')
        messages.success(request, 'You have singed up successfully.')
        return redirect('sign_in')
    if request.method == 'GET':
        #form = forms.SignUpForm()
        form = forms.CustomSignUpForm()
        return render(request, 'sign_up.html', {'form': form})


#@csrf_exempt
def front_page(request):
    try:
        #auth_check(request)
        without_auth_check(request)
    except PermissionDenied:
        return redirect('sign_in')
    available_items = models.Item.objects.filter(item_loaner__isnull=True)
    #print("front_page called with request",request,"fetched available_items",available_items)
    return render(request, "front_page.html", {
        "available_items": available_items,
        })
    
@csrf_exempt
def loan(request, item_id):

    try:
        #item = loan_check(request, item_id)
        item = without_loan_check(request, item_id)
    except PermissionDenied:
        return redirect('sign_in')
    except SuspiciousOperation:
        messages.error(request, 'The item is already loaned')
        return redirect('front_page')
    except models.Item.DoesNotExist:
        messages.error(request, 'There is no such item in the database')
        return redirect('front_page')
    if request.method == "GET":
        #print("loan",request.method,"called, rendering with item",item)
        return render(request, "confirmation.html", {
            "loan": True,
            "item": item,  
        })
    if request.method == "POST":
        choice = request.POST.get('choice')
        if choice == 'Yes':
            item.item_loaner = request.user
            item.save()
            messages.success(request, 'Loan success')
            #print("borrow",request.method,"called & update finished. Redirecting to front page")
        return redirect('front_page')
        

@csrf_exempt
def ret(request,item_id):
    try:
        #item = return_check(request, item_id)
        item = without_return_check(request, item_id)
    except PermissionDenied:
        return redirect('sign_in')
    except SuspiciousOperation:
        messages.error(request, 'The item is not in your possession')
        return redirect('front_page')
    except models.Item.DoesNotExist:
        messages.error(request, 'There is no such item in the database')
        return redirect('front_page')
    if request.method == "GET":
        #print("request",request.method,"called, rendering with item",item)
        return render(request, "confirmation.html", {
            "ret": True,
            "item": item,  
        })
    if request.method == "POST":
        choice = request.POST.get('choice')
        if choice == 'Yes':
            item.item_loaner = None
            item.save()
            messages.success(request, 'Item returned')
            #print("return",request.method,"called & update finished. Redirecting to front page")
        return redirect('front_page')

#@csrf_exempt
def loans(request):
    try:
        auth_check(request)
    except PermissionDenied:
        return redirect('sign_in')
    loaned_items = models.Item.objects.filter(item_loaner=request.user)
    return render(request, "loans.html", {
        "loaned_items": loaned_items,
    })

@csrf_exempt    
def sign_out(request):
    logout(request)
    messages.success(request, 'You signed out')
    return redirect('sign_in')
