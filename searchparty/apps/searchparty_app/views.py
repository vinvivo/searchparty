from django.shortcuts import render, HttpResponse, redirect
from .models import User
from django.contrib import messages
import bcrypt

def main(request):
    ''' Redirects localhost:8000/ to localhost:8000 '''
    return redirect('/')

def index(request):
    '''  '''
    return render(request, 'searchparty_app/index.html')

def login(request):
    ''' Renders /login URL '''
    return render(request, 'searchparty_app/login.html')

def register(request):
    errors = User.objects.user_validator(request.POST)
    if errors:
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        return redirect('/')
    else:
        # query for username
        q = User.objects.filter(username=request.POST['username'])
        if q.count() > 0:
            # check for existing user
            messages.error(request, "A user account with that username already \
            exists", extra_tags="username")
            return redirect('/')
        else:
            hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
            q = User.objects.create(name = request.POST['name'], username = request.POST['username'], password=hashed_pw)
            request.session['user_id'] = q.id
            request.session['username'] = q.username
            return redirect('/success')
    return redirect('/')

def log_in(request):
    # check user for that username
    # then check password
    found_users = User.objects.filter(username=request.POST['username'])
    if found_users.count() > 0:
        # check password
        found_user = found_users.first()
        if bcrypt.checkpw(request.POST['password'].encode(), found_user.password.encode()) is True:
            # log in user
            request.session['user_id'] = found_user.id  # user_id from username query
            request.session['username'] = found_user.username
            return redirect('/success')
        else:
            messages.error(request, "Login Failed", extra_tags="username")
            return redirect('/')
    else:
        messages.error(request, "Invalid login", extra_tags="username")
        return redirect('/')

def success(request):
    ''' Redirects user to /travels if user passes login() or register() '''
    return redirect('/travels')

def travels(request):
    ''' Renders /travels URL '''
    context = {
        # my_trips: Look for Trip objects that were posted by me
        "my_trips": Trip.objects.filter(poster__id = request.session['user_id']),
        # trips_i_joined: Look for Trip objects that have my session user_id on them (I joined them)
        "trips_i_joined": Trip.objects.filter(users__id = request.session['user_id']),
        # all_trip: Look for Trip objects that do not include my id as a joiner (exclude users__id = session[user_id]) and do not include my id as a poster (i.e., I'm not leading this trip)
        "all_trips": Trip.objects.exclude(users__id = request.session['user_id']).exclude(poster__id = request.session['user_id']),
        # poster_username: Look for User objects whose id matches my id
        "poster_username": User.objects.get(id = request.session['user_id']).username,
    }
    return render(request, 'searchparty_app/travels.html', context)

def post_trip(request):
    if request.method == "POST":
        errors = Trip.objects.basic_validator(request.POST)
        if errors:
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/post_trip')
        else:
            q = Trip.objects.create(destination = request.POST['destination'], description = request.POST['description'], date_start = request.POST['date_start'], date_end = request.POST['date_end'], poster = User.objects.get(id = request.session['user_id']))
            return redirect('/travels')
    else:
        return render(request, 'searchparty_app/add.html')

def join(request, id):  # here, id = trip_id
    if request.method == "POST":
        user_query = User.objects.get(id=request.session['user_id'])
        user_query.save()
        trip_query = Trip.objects.get(id=id)  # here, second id = trip_id
        trip_query.save()
        # child_query.related_name_that_allows_me_to_reach_into_parent_table.add(parent_query)
        trip_query.users.add(user_query)
        # check for success
        print "Added user #", request.session['user_id'], "to trip #", trip_query
        return redirect('/travels')
    else:
        return redirect('/travels')

def destination(request, id):  # here, id = trip_id
    context = {
        "joiners": User.objects.filter(trips__id = id),  # here, second id = trip_id; other users will be excluded
        "trip_info": Trip.objects.get(id = id), # here, second id = trip_id
    }
    print context
    return render(request, 'searchparty_app/destination.html', context)