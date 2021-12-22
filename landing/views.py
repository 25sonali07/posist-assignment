from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from .models import Channel, ChannelPost
from django.db.models import Count
import datetime

# Create your views here.
def home(request):
    user = request.user
    if (user.is_anonymous):
        return render(request, 'home.html')
    all_channel = Channel.objects.all()
    channels = []
    for chnl in all_channel:
        user_list = chnl.users.split(",")
        cur_user = str(request.user)
        if chnl.owner==request.user:
            channels.append(chnl)
        elif cur_user in user_list:
            channels.append(chnl)
    return render(request, 'home.html', {"channels":channels, "channel":True, "post":False})


def dashboard(request):
    if (request.user.is_anonymous):
        return render(request, 'error.html')

    all_channels = Channel.objects.all()
    all_Posts = ChannelPost.objects.all()
    all_users = User.objects.all()

    if request.method == 'POST':
        all_channels = all_channels.filter(created_date__range=[request.POST["start"], request.POST["end"]])
        all_Posts = all_Posts.filter(created_date__range=[request.POST["start"], request.POST["end"]])

    top_channel_post = {}
    for channel in all_channels:
        post_count = all_Posts.filter(channel=channel).count()
        name = channel.name
        top_channel_post[name]=post_count
    channel_post_dash = list(reversed(sorted(top_channel_post.items(), key=lambda kv: [kv[1], kv[0]])))[:5]

    top_user = {}
    for user in all_users:
        post_count = all_Posts.filter(user=user).count()
        name = user.first_name
        top_user[name] = post_count
    top_user_dash = list(reversed(sorted(top_user.items(), key=lambda kv: [kv[1], kv[0]])))[:5]
    top_region_dash = list(all_users.values('last_name').annotate(count= Count('last_name')).order_by('-count'))[:5]

    all_tags = {}
    for i in all_channels:
        temp = i.tags.split(",")
        for tag in temp:
            if tag in all_tags:
                all_tags[tag]+=1
            else:
                all_tags[tag]=1
    top_tags_dash = list(reversed(sorted(all_tags.items(), key=lambda kv: [kv[1], kv[0]])))[:5]
    context = {"channel_post": channel_post_dash, "top_user": top_user_dash, "region":top_region_dash, "top_tags":top_tags_dash, "channel":True}
    return render(request, 'dashboard.html', context=context)


def handleLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome Back {username} !!")
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials!! Please try again later.")
            return redirect('home')
    return render(request,'error.html')


def handleSignup(request):
    if request.method == 'POST':
        region = request.POST['region']
        fname = request.POST['name']
        email = request.POST['email']
        pass1 = request.POST['password']
        pass2 = request.POST['conpassword']

        if pass1 != pass2:
            messages.error(request, "Password and Confirm Password not match.")
            return redirect('home')       

        myuser = User.objects.create_user(email, email, pass1)
        myuser.first_name = fname
        myuser.last_name = region
        myuser.save()

        user = authenticate(username = email, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, "You are Successfully Signed-Up !!")
            return redirect('home')

        messages.success(request, "Your Account has been Successfully Created !!!")
        return redirect('home')
    else:
        return render(request,'error.html')


def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully Logged out")
    return redirect('home')


class ChannelView(View):

    def get(self, request):
        if (request.user.is_anonymous):
            return render(request, 'error.html')
        channels = Channel.objects.filter(owner=request.user)
        return render(request, 'home.html', {"channels":channels})

    def post(self, request):
        if (request.user.is_anonymous):
            return render(request, 'error.html')
        name = request.POST['name']
        desc = request.POST['desc']
        users = request.POST['users']
        tags = request.POST['tags']
        channel = Channel(name=name, description=desc, users=users, tags=tags, owner=request.user)
        channel.save()

        messages.success(request, "Channel Created Successfully!!")
        return redirect('home')


class PostView(View):

    def get(self, request):
        if (request.user.is_anonymous):
            return render(request, 'error.html')
        channels = Channel.objects.filter(owner=request.user)
        return render(request, 'home.html', {"channels":channels})

    def post(self, request):
        if (request.user.is_anonymous):
            return render(request, 'error.html')
        post_content = request.POST['post']
        user = request.user
        try:
            channel = Channel.objects.get(id=request.POST['channel'])
        except Channel.DoesNotExist:
            messages.error(request, "Seems like somethingw wrong with channel!!")
            return render(request, 'error.html')
        
        post_instance = ChannelPost(post_data=post_content, user=user, channel=channel)
        post_instance.save()

        messages.success(request, "Post Created Successfully!!")
        return redirect('Open Channel', pk=request.POST['channel'])


def openChannel(request, pk):
    if (request.user.is_anonymous):
        return render(request, 'error.html')
    channel = Channel.objects.get(id=pk)
    user_list = channel.users.split(",")
    cur_user = str(request.user)
    allow_post = False
    print(cur_user, user_list)
    if cur_user in user_list:
        allow_post = True
    elif channel.owner == request.user:
        allow_post = True
    else:
        messages.error(request, "You Don't have permission for this group...")
        return redirect('home')
    posts = ChannelPost.objects.filter(channel=channel).order_by("-created_date")
    return render(request, 'channel.html', {"posts":posts, "channel":False, "post":allow_post, "channel_id":pk})