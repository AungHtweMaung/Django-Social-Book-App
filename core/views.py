from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from .forms import SettingForm
from itertools import chain
import random

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_profile = Profile.objects.filter(user=request.user).first()

    user_following_list = []
    feed = []

    # current user သည် follower ဖြစ်မယ်။ သူက ဘယ်သူ့ကို follow လုပ်ထားတယ်ဆိုတာရမယ်။ 
    # အဲ့တော့ current user က follow လုပ်ထားတဲ့ user တွေရဲ့ information တွေယူပြီး current user ရဲ့ home page မှာပြပေးတယ် 
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    # print(user_following) 
    # follow လုပ်ထားတဲ့ user object list ကြီးကို တစ်ခုချင်း loop ပတ်ပြီး field တွေကို လိုသလို သုံးလို့ရတယ် 
    for users in user_following:
        user_following_list.append(users.user) # users.user => follow လုပ်ထားတဲ့ user တွေရဲ့ name ကိုထည့်ပေးလိုက်တာ

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(post_owner=usernames)
        # print(feed_lists)
        feed.append(feed_lists) # list ထဲမှာ query set တွေအနေနဲ့ ဝင်သွားတာ    
    feed_list = list(chain(*feed))  # list ထဲမှာ post item တစ်ခုချင်းအနေနဲ့ ဝင်သွားတာ

    # user suggestion list 
    all_users = User.objects.all()
    user_following_all = []
    # user
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    # print(user_following_all)# user follow လုပ်ထားတဲ့ user object တွေကို list ထဲ ထည့်ပေးလိုက်တယ် 

    # user follow လုပ်မထားတဲ့ user တွဗကို ပြမယ်။ current user ကိုလည်း exclude လုပ်တယ်။ 
    new_suggestions_list = [x for x in list(all_users) if x not in user_following_all]
    print(new_suggestions_list) 
    current_user = User.objects.get(username=request.user.username)
    final_suggestions_list = [x for x in new_suggestions_list if x != current_user]
    
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)


    suggesstions_username_profile_list = list(chain(*username_profile_list))

    return render(request, "index.html", {
            "user_profile": user_profile,
            "posts": feed_list,
            "suggesstions_username_profile_list": suggesstions_username_profile_list[:4],
        })

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        username = request.POST["username"]
        # username__icontains => User model ထဲမှာရှိတဲ့ name တွေ
        # form က post method ကလာတဲ့ value username က 
        # Case Insensitive containment ကို စစ်တာ
        if username != "":
            username_object = User.objects.filter(username__icontains=username)
            print(username_object)

            username_profile = []
            username_profile_list = []

            for users in username_object:
                username_profile.append(users.id)
                # print(username_profile)

            # user object  ထဲက id နဲံ profile ထဲမှာရှိတဲ့ user တွေကို access လုပ်တာ
            for ids in username_profile:
                profile_lists = Profile.objects.filter(user=ids)
                username_profile_list.append(profile_lists)
            
            username_profile_list = list(chain(*username_profile_list))
            print(username_profile_list)
        
            context = {
                "user_object": user_object,
                "user_profile": user_profile,
                "old_value": username,
                "username_profile_list": username_profile_list,
            }
            return render(request, "search.html", context)
        else:
            return render(request, "search.html", {
                "user_object": user_object,
                "user_profile": user_profile,
            })
    return render(request, "search.html")


@login_required(login_url='signin')
def upload(request):
    
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get("image_upload")
        caption = request.POST["caption"]

        print(image)

        if image == None:
            return redirect("/")
        else:
            user_model = User.objects.get(username=request.user.username)
            new_post = Post.objects.create(user=user_model, post_owner=user, image=image, caption=caption)
            new_post.save()
            
            return redirect("/")

    else:
        return redirect("/")


@login_required(login_url='signin')
def like_post(request):
    """
    Like တွေအတွက် database table သက်သက် create လုပ်ပီး သိမ်းထားတယ် 
    current user ရဲ့ username ကိုယူတယ်။ like လုပ်လိုက်တဲ့ post_id ကို backend ကိုလှမ်းပို့တယ် 
    like_filter သည် LikePost Model ထဲမှာ current user liked ရှိလားကြည့်တယ်
    မရှိရင် like btn ကို click လိုက်ရင် LikePost table ထဲမှာ သိမ်းပေးသွားတယ် 
    ရှိရင် Like ပြန်ဖြုတ်တယ် ။ 
    """
    
    username = request.user.username 
    post_id = request.GET.get("post_id")
    print(post_id)
    # post is to get number of likes from post model
    post = Post.objects.get(id=post_id)
    # check user's like exists or not.
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect("/")
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect("/")


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk) # User Model ထဲမှာ register လုပ်ထားတဲ့ name တစ်ခုခုကို pk အနေနဲ့ပေးလိုက်တယ် 
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.filter(user=user_object.id) # user_obj ထဲက id နဲ့ post ထဲမှာ Foreign key ရဲ့ user နဲ့ ညီပေးလိုက်တယ် 
    user_post_length = len(posts)
    
    follower = request.user
    user = pk 
    # change button text dynamically
    if FollowersCount.objects.filter(follower=follower, user=pk).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
    
    # pk သည် name တွေဖြစ်မယ်။ FollowersCount ထဲမှာ follower, user နဲ့ follower ကို တိုက်စစ်ပီး  follower, user ကိုရယူတယ်
    user_followers = len(FollowersCount.objects.filter(user=pk))  # ငါတို့ကို သူများတွေက follow လုပ်ထားတဲ့ counts 
    user_followings = len(FollowersCount.objects.filter(follower=pk))  # ငါတို့ကနေ သူများကို follow လုပ်ထားတဲ့ counts 

    context = {
        "user_profile": user_profile,
        "user_object": user_object,
        "posts": posts,
        "user_post_length": user_post_length,
        "user_followers": user_followers,   
        "user_followings": user_followings,
        "button_text": button_text,
    }
    return render(request, "profile.html", context)



@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower = request.POST["follower"]
        user = request.POST["user"]
        # follower count tabel ထဲမှာ follwer လုပ်လိုက်တာနဲ့ ထည့်ပေးသွားမှာ ရှိပြီးသားဆို ဖြုတ်မှာ၊ မရှိရင် create လုပ်ပေးသွားမှာ 
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect("profile", user) # or return redirect("profile/" + user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect("profile", user)
    else:
        return redirect("/")


@login_required(login_url='signin')
def settings(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        if request.FILES.get('profile_img') == None:
            profile_img = user_profile.profile_img
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profile_img = profile_img
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            return redirect("settings")

        if request.FILES.get('profile_img') != None:
            profile_img = request.FILES.get("profile_img")
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profile_img = profile_img
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            return redirect("settings") 

    return render(request, "settings.html", {
        "user_object": user_object,
        "user_profile": user_profile,
    })

# @login_required(login_url='signin')
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists") 
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists") 
                return redirect("signup")
            elif " " in username:
                messages.info(request, "Username can't contain space.")
                return redirect("signup")
            else:
                user = User.objects.create_user(username=username, \
                                                email=email,
                                                password=password)
                
                user.save()

                # log user in and redirect to settings page
                user_login = authenticate(request, username=username, password=password)
                auth_login(request, user_login)
                
                # create a profile for the new user တစ်ခါတည်း Profile model ကိုခေါ်ပီး directly create လုပ်လို့ရတယ်
                # new_profile = Profile.objects.create(user=user, id_user=user.id)
                # new_profile.save()

                # This is the creating user profile by using model
                # user_model = User.objects.get(username=username)
                # # We want to give user and id as a default while we are creating profile model for that user.
                # new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                # new_profile.save() 
                return redirect("/")
    
        else:
            messages.info(request, "Password didn't match")
            return redirect("signup")     
    else:
        render(request, "signup.html")
    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        user = authenticate(request, username=username, password=password)
        
        if user != None:
            auth_login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Username and Password didn't match.")
            return redirect("signin")

    return render(request, "signin.html")

@login_required(login_url='signin')
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)

        return redirect("signin")