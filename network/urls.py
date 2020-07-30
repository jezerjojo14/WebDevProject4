
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("following/<int:page>", views.following_page, name="following_page"),
    path("<int:page>", views.page, name="page"),
    path("user/<str:username>/<int:page>", views.profile_page, name="profile_page"),
    path("toggle_like", views.toggle_like, name="toggle_like"),
    path("toggle_follow", views.toggle_follow, name="toggle_follow"),
    path("user/<str:username>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.new_post, name="new_post"),
    path("edit", views.edit_post, name="edit_post")
]
