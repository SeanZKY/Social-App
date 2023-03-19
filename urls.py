from django.urls import path
from . import views


urlpatterns = [
    path('signin/', views.signin, name='Log in'),
    path('signup/', views.signup, name="signup"),
    path('site/', views.site, name="site"),
    path('pfp/', views.pfp, name="pfp"),
    path('newpost/', views.newpost, name="newpost"),
    path('myposts/', views.myposts, name="myposts")

]
