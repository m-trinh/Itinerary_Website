from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from itinerary.models import Trip, Day, Item, User
from itinerary.views.forms import CreateTripForm
from datetime import timedelta
from rest_framework import viewsets
from django.views.decorators.csrf import ensure_csrf_cookie
from itinerary.views.serializers import TripSerializer, DaySerializer, ItemSerializer, UserSerializer
import facebook

def index(request):
    return render(request, 'home.html')

def createTrip(request):
    if request.method == 'POST':
        #Get information from form and validate
        form = CreateTripForm(request.POST)
        if form.is_valid():
            creator = User.objects.get(fb_id=request.session['fb_id'])
            location = form.cleaned_data['location']
            trip_name = form.cleaned_data['trip_name']
            description = form.cleaned_data['description']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            public_level = form.cleaned_data['public']

            #If no trip name is given, use the lcoation as the name
            if not trip_name:
                trip_name = location

            #Create the trip
            trip = Trip(creator=creator, location=location, trip_name=trip_name, description=description, start_date=start_date, end_date=end_date, public_level=public_level)
            trip.save()

            #For each day of the trip, create a day object
            trip_duration = (end_date - start_date).days
            increment = timedelta(days=1)
            current_day = start_date
            day = Day(date=current_day, trip=trip)
            day.save()

            for num in range(0, trip_duration):
                current_day = current_day + increment
                day = Day(date=current_day, trip=trip)
                day.save()

            #Once trip is created, show it
            return redirect('showTrip', tripID=trip.id)

    else:
        #Show the trip creation form
        form = CreateTripForm()
        return render(request, 'createTrip.html', {'form': form})

def showAllTrips(request):
    #For development purposes only - Should not be in final product
    trips = Trip.objects.all()
    return render(request, 'allTrips.html', {'trips': trips})

@ensure_csrf_cookie
def showTrip(request, tripID):
    #TODO: Only allow those who have permission edit to edit
    error = None
    try:
        trip = Trip.objects.get(id=tripID)
        #Check to see if user can access trip
        response = canViewTrip(request, trip)
        if response == 'Can View' or response == 'Can Edit':
            #Fetch day and item information for the trip
            days = Day.objects.filter(trip_id=tripID).order_by('date')
            for day in days:
                items = Item.objects.filter(day_id=day.id)
                day.items = items
            return render(request, 'showTrip.html', {'trip': trip, 'days': days})
        else:
            #If user can't access trip
            return render(request, 'showTrip.html', {'error': response})
    except Trip.DoesNotExist:
        #If trip does not exist
        error = 'This trip does not exist'
        return render(request, 'showTrip.html', {'error': error})

def canViewTrip(request, trip):
    fb_id = None
    if 'fb_id' in request.session:
        fb_id = int(request.session['fb_id'])
        #User is the creator
        if fb_id == trip.creator.fb_id:
            return 'Can Edit'

        #Trip has been shared with the User
        shared = trip.shared_users.only('fb_id')
        for user in shared:
            if fb_id == user.fb_id:
                return 'Can Edit'

        #User is friends with the trip creator
        if trip.public_level == 'F' and 'access_token' in request.session:
            graph = facebook.GraphAPI(access_token=request.session['access_token'], version='2.7')
            friends = graph.get_connections(id=request.session['fb_id'], connection_name='friends')
            for user in friends['data']:
                if int(user['id']) == trip.creator.fb_id:
                    return 'Can View'

    #The trip is public
    if trip.public_level == 'E':
        return 'Can View'

    #User does not have access to the trip
    return 'You do not have access to this trip'

def viewMyTrips(request):
    #TODO: Distinguish between past and future trips
    #Get user, then search for trips created by that user
    if 'fb_id' in request.session:
        fb_id = int(request.session['fb_id'])
        user = User.objects.get(fb_id=fb_id)
        trips = Trip.objects.filter(creator=user);
        return render(request, 'myTrips.html', {'trips': trips})
    return render(request, 'error.html')

def getFriends(request):
    #Need access token to get friends - Make sure it isn't expired
    if 'fb_id' in request.session and 'access_token' in request.session:
        fb_id = int(request.session['fb_id'])
        trip = Trip.objects.get(id=request.POST.get('trip_id', '0'))
        #Check again to make sure user is creator
        if fb_id == trip.creator.fb_id:
            graph = facebook.GraphAPI(access_token=request.session['access_token'], version='2.7')
            #Get friends using Graph API
            friends = graph.get_connections(id=fb_id, connection_name='friends')
            #Create json object with arrays of friends that have and have not been given access to edit trip
            friends_json = {}
            friends_json['shared'] = []
            friends_json['unshared'] = []
            #Get shared users for trip
            shared = trip.shared_users.only('fb_id')
            #Add friend id to the correct category
            for friend in friends['data']:
                unshared = True
                for user in shared:
                    if int(friend['id']) == user.fb_id:
                        friends_json['shared'].append(friend)
                        unshared = False
                        break
                if unshared:
                    friends_json['unshared'].append(friend)
            return JsonResponse(friends_json)

def shareWithFriends(request):
    if 'fb_id' in request.session:
        fb_id = int(request.session['fb_id'])
        trip = Trip.objects.get(id=request.POST.get('trip_id', '0'))
        #Check again to make sure user is creator
        if fb_id == trip.creator.fb_id:
            id_list = request.POST.getlist('id_list[]', '0')
            #Clear all the shared users - In case user wants to remove permissions for someone
            trip.shared_users.clear()
            if id_list != '0':
                for id in id_list:
                    #Add users to shared
                    user = User.objects.get(fb_id=int(id))
                    trip.shared_users.add(user)
            return HttpResponse("Friends added to trip")

def addItem(request):
    day_id = request.POST.get('day_id')
    day = Day.objects.get(id=day_id)

    highest_position = Item.objects.filter(day_id=day_id).order_by('-item_position')[:1]
    next_position = 1
    if highest_position:
        next_position = highest_position[0].item_position + 1

    item = Item.objects.create(item_name=request.POST.get('item_name'), item_position=next_position, day=day)
    #item.save()
    print(item)

    return JsonResponse(dict(item))

def items(request):
    if request.method == 'POST':
        print(request.POST)
        data = request.POST

        serializer = ItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def login(request):
    if request.method == 'POST':
        #Get information from request
        fb_id = request.POST.get('fb_id', '0')
        email = request.POST.get('email', '0')
        first_name = request.POST.get('first_name', '0')
        last_name = request.POST.get('last_name', '0')
        access_token = request.POST.get('access_token', '0')
        #If user exists and their info has changed, update it
        try:
            existingUser = User.objects.get(fb_id=fb_id)
            if existingUser.email != email or existingUser.first_name != first_name or existingUser.last_name != last_name:
                existingUser.update(email=email, first_name=first_name, last_name=last_name)
        except:
            #User does not exist, so add to database
            User.objects.create(fb_id=fb_id, email=email, first_name=first_name, last_name=last_name)
        finally:
            #Update session
            request.session['fb_id'] = fb_id
            request.session['access_token'] = access_token
            return HttpResponse("Logged In")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
