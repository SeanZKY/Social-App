from pathlib import Path
from django.shortcuts import render
from .HelperFunctions import *
from .models import *
from django.db.models.base import ObjectDoesNotExist

LOGIN_TIME = 1000
DATABASE_USERNAME_INDEX = 2
FIRST_INDEX = 0
ZERO_MATCHES = 0

#  This file contains the function that the requests are sent to


def signin(request):  # sign in page
    if request.method == "POST":
        runner = ManageDatabase()
        if runner.user_exists(request.POST["gmail"], request.POST["password"]):  # details are correct
            response = redirect("/site/")
            response.set_cookie('username', runner.find_username(request.POST["gmail"])
                                [FIRST_INDEX][DATABASE_USERNAME_INDEX], max_age=LOGIN_TIME)
            return response
        else:  # user doesn't exist
            temp = loader.get_template("TwitterLogin.html")
            context = {'connect_error': 'wrong username or password'}
            return HttpResponse(temp.render(context, request))

    elif request.COOKIES.get('username') is not None:
        response = redirect("/site/")   # user is signed in
        return response

    return render(request, "TwitterLogin.html")


def signup(request):  # sign up page
    if request.method == "POST":
        runner = ManageDatabase()
        if not runner.unavailable_user(request.POST["gmail"], request.POST["username"]):  # if details aren't taken
            runner.insert_user(request.POST["gmail"], request.POST["password"], request.POST["username"])
            runner.conn.commit()
            return render(request, "SuccessfulSubmission.html")
    return render(request, "TwitterSignUp.html")


def site(request):  # The main site + searching users page - view user defines the search
    runner = ManageDatabase()
    if request.COOKIES.get('username') is None or len(runner.find_from_name(request.COOKIES.get('username'))) == 0:
        return redirect("/signin/")
    if 'view_user' not in list(request.GET.keys()):  # this is either a post or just regular site access
        if request.method == "POST":
            if "accept_user" in list(request.POST.keys()) and request.COOKIES.get('username') in \
                    runner.ret_data("requesting", request.POST["accept_user"]):
                runner.remove_data("requested", str(request.POST["accept_user"]), request.COOKIES.get('username'))
                runner.remove_data("requesting", request.COOKIES.get('username'), str(request.POST["accept_user"]))
                runner.add_data("following", request.COOKIES.get('username'), str(request.POST["accept_user"]))
                runner.add_data("followers", str(request.POST["accept_user"]), request.COOKIES.get('username'))
            elif "decline_user" in list(request.POST.keys()):
                runner.remove_data("requested", str(request.POST["decline_user"]), request.COOKIES.get('username'))
                runner.remove_data("requesting", request.COOKIES.get('username'), str(request.POST["decline_user"]))
            elif "cancel_follower" in list(request.POST.keys()):
                runner.remove_data("following", request.COOKIES.get('username'), str(request.POST["cancel_follower"]))
                runner.remove_data("followers", str(request.POST["cancel_follower"]), request.COOKIES.get('username'))
            elif "delete_post" in list(request.POST.keys()):
                try:
                    post = Post.objects.get(id=request.POST["delete_post"])
                    os.remove(Path(post.file.name))
                    post.delete()
                except ObjectDoesNotExist:
                    pass
            elif "comment" in list(request.POST.keys()):
                comment_post = Post.objects.get(id=int(request.POST["post"]))
                comment = Comment(post=comment_post, text=request.COOKIES.get('username') + ":" +
                                  request.POST["comment"], username=request.COOKIES.get('username'))
                comment.save()
        return site_posts(request, request.COOKIES.get('username'), 'twitter.html')

    user_name = request.COOKIES.get('username')
    follow_name = str(request).split("?view_user=")[1][0:-2]
    if follow_name == user_name:  # user searched himself
        return enter_site('twitter.html', request)

    status = runner.find_status(user_name, follow_name)
    helper_dict = {-1: "Follow", 3: "Following", 4: "Request Sent"}
    status = helper_dict[status]
    if request.method == "POST":
        if "comment" in list(request.POST.keys()):
            comment_post = Post.objects.get(id=int(request.POST["post"]))
            comment = Comment(post=comment_post, text=request.COOKIES.get('username') + ":" +
                              request.POST["comment"], username=request.COOKIES.get('username'))
            comment.save()
            return enter_site('twitter.html', request)
        former_status = str(request.POST["status"])  # user request
        if former_status == "Follow":
            status = "Request Sent"
        else:
            status = "Follow"
        if len(runner.find_from_name(follow_name)) == ZERO_MATCHES:
            return enter_site('twitter.html', request)

        if former_status == "Following":
            runner.remove_data("following", follow_name, user_name)
            runner.remove_data("followers", user_name, follow_name)

        elif former_status == "Follow":
            runner.add_data("requesting", follow_name, user_name)
            runner.add_data("requested", user_name, follow_name)

        elif former_status == 'Request Sent':
            runner.remove_data("requesting", follow_name, user_name)
            runner.remove_data("requested", user_name, follow_name)

    if len(runner.find_from_name(request.GET['view_user'])) == ZERO_MATCHES:
        return enter_site('twitter.html', request)
    if status == "Following":
        return site_posts(request, request.GET['view_user'], 'userPosts.html', {'user_search': request.GET['view_user'],
                                                                                'user_status': status})
    else:
        return enter_site('userPosts.html', request, {'user_search': request.GET['view_user'],
                                                      'user_status': status})


def pfp(request):  # let the user choose a profile picture
    if request.COOKIES.get('username') is None \
            or len(ManageDatabase().find_from_name(request.COOKIES.get('username'))) == 0:
        return redirect("/signin/")

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        file_type = request.FILES['file'].name.split(".")[-1]
        request.FILES['file'].name = request.COOKIES.get('username') + "-" + \
            "ProfilePicture" + "."
        if os.path.exists(request.COOKIES.get('username')) and Path(request.COOKIES.get('username') + "//" +
                                                                    request.FILES['file'].name + "jpg").is_file():
            os.remove(Path(request.COOKIES.get('username') + "//" + request.FILES['file'].name + "jpg"))
            for profile_pic in Blog.objects.all():
                if request.COOKIES.get('username') + "/" + request.COOKIES.get('username') + "-" + "ProfilePicture." \
                        + "jpg" == profile_pic.file.name:
                    profile_pic.delete()

        if os.path.exists(request.COOKIES.get('username')) and Path(request.COOKIES.get('username') + "//" +
                                                                    request.FILES['file'].name + "png").is_file():
            os.remove(Path(request.COOKIES.get('username') + "//" + request.FILES['file'].name + "png"))
            for profile_pic in Blog.objects.all():
                if request.COOKIES.get('username') + "/" + request.COOKIES.get('username') + "-" + "ProfilePicture." \
                        + "png" == profile_pic.file.name:
                    profile_pic.delete()
        request.FILES['file'].name += file_type
        if form.is_valid():
            helper = form.save(commit=False)
            helper.username = request.COOKIES.get('username')
            helper.save()
            return enter_site("Pfp.html", request, {'form': form})
    else:
        form = BlogForm()
        return enter_site("Pfp.html", request, {'form': form})


def newpost(request):  # receive a post from the user
    if 'view_user' in list(request.GET.keys()):
        return redirect("/site/?view_user=" + request.GET['view_user'])
    if request.COOKIES.get('username') is None or \
            len(ManageDatabase().find_from_name(request.COOKIES.get('username'))) == 0:
        return redirect("/signin/")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        request.FILES['file'].name = request.COOKIES.get('username') + "-" + \
            "media0" + "." + request.FILES['file'].name.split(".")[-1]
        while Path(request.COOKIES.get('username') + "//" + request.FILES['file'].name).is_file():
            num = int(request.FILES['file'].name.split(".")[-2][-1]) + 1
            request.FILES['file'].name = request.FILES['file'].name.split(".")[-2][0:-1] + str(num) \
                + "." + request.FILES['file'].name.split(".")[-1]

        if form.is_valid():
            helper = form.save(commit=False)
            helper.username = request.COOKIES.get('username')
            helper.save()

            return enter_site("post.html", request, {'form': form})
    else:
        form = PostForm()
        return enter_site("post.html", request, {'form': form})
    return enter_site('post.html', request)


def myposts(request):  # user posts redirect
    if 'view_user' in list(request.GET.keys()):
        return redirect("/site/?view_user=" + request.GET['view_user'])
    return redirect("/site")
