import base64
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from .Databases import *
from .models import *

#  this file has functions that help views to preform certain actions


def to_base_64(file):  # turn file to base_64
    try:
        with open(file, "rb") as file:
            data = base64.b64encode(file.read()).decode('utf-8')
            return data
    except FileNotFoundError:
        return ""


def remove_blank_from_lst(lst):  # remove blanks from lst
    for x in lst:
        if x == "":
            lst.remove(x)
            return


def enter_site(page, request, adder=None):  # return details necessary to every url (not including sign-in or sign-up
    runner = ManageDatabase()
    if request.COOKIES.get('username') is None:
        return redirect("/signin/")
    temp = loader.get_template(page)
    requested_lst = runner.ret_data("requested", request.COOKIES.get('username')).split(",")
    remove_blank_from_lst(requested_lst)
    following_lst = runner.ret_data("following", request.COOKIES.get('username')).split(",")
    remove_blank_from_lst(following_lst)
    followers_lst = runner.ret_data("followers", request.COOKIES.get('username')).split(",")
    remove_blank_from_lst(followers_lst)

    context = {'user_input': request.COOKIES.get('username'), "requests_lst": requested_lst,
               "following_lst": following_lst, "followers_lst": followers_lst}
    if adder is not None:
        context.update(adder)
    return HttpResponse(temp.render(context, request))


def site_posts(request, user, ret_site, adder=None):  # sent the post of the user that the function got
    posts = Post.objects.filter(username=user)
    img_lst = []
    comments = []
    id_lst = []
    for x in posts:
        img_lst.append(to_base_64(x.file.url[1:]))
        id_lst.append("post" + str(x.id))
    posts = reversed(posts)
    img_lst.reverse()
    id_lst.reverse()

    context = {"posts_lst": zip(posts, img_lst, id_lst)}

    user_pfp = ProfilePicture.objects.filter(username=user)
    if len(user_pfp) == 0:
        context['Pfp'] = to_base_64("static//no_user.jpg")
    else:
        user_pfp = user_pfp[0]
        context['Pfp'] = to_base_64(user_pfp.file.url[1:])
    for x in Comment.objects.all():
        comments.append(x)
    context["comments"] = comments
    context["update_date"] = str(datetime.now())

    if adder is not None:
        context.update(adder)
    return enter_site(ret_site, request, context)
