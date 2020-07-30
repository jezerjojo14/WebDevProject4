from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post

class NewPost(forms.Form):
    auto_id = False
    content = forms.CharField(label="", widget=forms.Textarea(), max_length=400, required=True)
    # attrs={'rows':4, 'cols':75}

#Index page


def index(request, page=1):
    p=Paginator(Post.objects.all().order_by("-time"), 10)
    if page not in p.page_range:
        raise Http404
    return render(request, "network/index.html", {"form": NewPost().as_p(), "posts": p.page(page), "page": page, "pagecount": p.num_pages})

def page(request, page):
    if page==1:
        return HttpResponseRedirect(reverse("index"))
    return index(request, page)

#Followed Account Posts


@login_required
def following(request, page=1):
    p=Paginator(Post.objects.all().filter(user__in = request.user.following.all()).order_by("-time"), 10)
    if page not in p.page_range:
        raise Http404
    return render(request, "network/following.html", {"posts": p.page(page), "page": page, "pagecount": p.num_pages})

def following_page(request, page):
    if page==1:
        return HttpResponseRedirect(reverse("following"))
    return following(request, page)

#Registration and login


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })
        if len(password) < 8:
            return render(request, "network/register.html", {
                "message": "Password must have at least 8 characters."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


#Profile


def profile(request, username, page=1):
    user=User.objects.get(username=username)
    posts=Paginator(Post.objects.all().filter(user=user).order_by("-time"), 10)
    if page not in posts.page_range:
        raise Http404
    # posts=Post.objects.all().filter(user=user).order_by("-time")
    following=user.following.all().count()
    followers=user.user_set.all().count()
    return render(request, "network/profile.html", {"profile_user": user, "posts": posts.page(page), "followers": followers, "following": following, "page": page, "pagecount": posts.num_pages})

def profile_page(request, username, page):
    if page==1:
        return HttpResponseRedirect(reverse("profile", kwargs={'username':username}))
    return profile(request, username, page)


@csrf_exempt
@login_required
def toggle_follow(request):
    data=json.loads(request.body)
    logged_username=request.user
    profile_username=data['profile']
    logged_user=User.objects.get(username=logged_username)
    profile_user=User.objects.get(username=profile_username)
    follow=data['follow']
    if logged_user!=profile_user:
        if follow and (profile_user not in logged_user.following.all()):
            logged_user.following.add(profile_user)
        if not(follow) and (profile_user in logged_user.following.all()):
            logged_user.following.remove(profile_user)
        logged_user.save()
        print('{"follow":'+str(int(profile_user in logged_user.following.all()))+'}')
        return HttpResponse('{"follow":'+str(int(profile_user in logged_user.following.all()))+'}', status=200)
    else:
        return HttpResponse(status=403)

#Posts


def new_post(request):
    p=Post(content=(request.POST["content"]).replace("<", "&lt;").replace("\n","<br>").replace("\r","<br>"), user=request.user)
    p.save()
    return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def edit_post(request):
    data=json.loads(request.body)
    p=Post.objects.get(id=data["id"])
    if p.user==request.user:
        p.content=data["content"]
        p.edited=True;
        p.save();
        return HttpResponse('{"content":"'+p.content+'"}', status=200)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@login_required
def toggle_like(request):
    data=json.loads(request.body)
    postid=data['p']
    p=Post.objects.get(pk=postid)
    user=request.user
    like=data['like']
    print(p, user, like)
    if like and (user not in p.likes.all()):
        p.likes.add(user)
    if not(like) and (user in p.likes.all()):
        p.likes.remove(user)
    p.save()
    print((HttpResponse('{"like":'+str(int(user in p.likes.all()))+'}', status=200)).content)
    return HttpResponse('{"like":'+str(int(user in p.likes.all()))+'}', status=200)
