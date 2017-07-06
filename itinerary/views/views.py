from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from itinerary.models import Trip, Day, Item, User
from itinerary.views.forms import CreateTripForm
from itinerary.views.api_ids import Ids
from datetime import timedelta, date
from rest_framework import viewsets
from django.views.decorators.csrf import ensure_csrf_cookie
from itinerary.views.serializers import TripSerializer, DaySerializer, ItemSerializer, UserSerializer
import requests
import facebook
import json

def index(request):
    return render(request, 'home.html')

def createTrip(request):
    if request.method == 'POST':
        #Get information from form and validate
        form = CreateTripForm(request.POST)
        if form.is_valid():
            creator = User.objects.get(fb_id=request.session['fb_id'])
            location = form.cleaned_data['location']
            longitude = form.cleaned_data['longitude']
            latitude = form.cleaned_data['latitude']
            trip_name = form.cleaned_data['trip_name']
            description = form.cleaned_data['description']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            public_level = form.cleaned_data['public']

            #If no trip name is given, use the lcoation as the name
            if not trip_name:
                trip_name = location

            #Create the trip
            trip = Trip(creator=creator, location=location, longitude=longitude, latitude=latitude, trip_name=trip_name, description=description, start_date=start_date, end_date=end_date, public_level=public_level)
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
        if response:
            request.session['current_trip'] = tripID
            request.session['trip_permission'] = response
            #Fetch day and item information for the trip
            days = Day.objects.filter(trip_id=tripID).order_by('date')
            for day in days:
                items = Item.objects.filter(day_id=day.id).order_by('item_position')
                day.items = items
            return render(request, 'showTrip.html', {'trip': trip, 'days': days, 'permissions': response})
        else:
            #If user can't access trip
            return render(request, 'showTrip.html', {'error': 'You do not have access to this trip'})
    except Trip.DoesNotExist:
        #If trip does not exist
        error = 'This trip does not exist'
        return render(request, 'showTrip.html', {'error': error})

def canViewTrip(request, trip):
    if 'fb_id' in request.session:
        fb_id = int(request.session['fb_id'])
        #User is the creator
        if fb_id == trip.creator.fb_id:
            return 'Creator'

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
    return False

def viewMyTrips(request):
    #Get user, then search for trips created by that user
    if 'fb_id' in request.session:
        fb_id = int(request.session['fb_id'])
        user = User.objects.get(fb_id=fb_id)
        #Current trips are in progress, with a start date before today and end date after today
        current_trips = Trip.objects.filter(creator=user).filter(start_date__lte=date.today()).filter(end_date__gte=date.today()).only('id', 'trip_name', 'start_date', 'end_date').order_by('start_date')
        #Future trips have start date after today
        future_trips = Trip.objects.filter(creator=user).filter(start_date__gte=date.today()).only('id', 'trip_name', 'start_date', 'end_date').order_by('start_date')
        return render(request, 'myTrips.html', {'current_trips': current_trips, 'future_trips': future_trips})
    return render(request, 'error.html')

def viewPastTrips(request):
    #Only load in past trips upon request
    if 'fb_id' in request.session:
        fb_id = int(request.session['fb_id'])
        user = User.objects.get(fb_id=fb_id)
        #Get trips with an end date that is after today
        trips = Trip.objects.filter(creator=user).filter(end_date__lt=date.today()).order_by('-end_date')
        if trips.count() != 0:
            #Convert queryset into a serializable object
            response = {}
            response['data'] = []
            for trip in trips:
                data = {'id': trip.id, 'trip_name': trip.trip_name, 'start_date': trip.start_date, 'end_date': trip.end_date}
                response['data'].append(data)
            return JsonResponse({'trips': response})
        else:
            #If there are no past trips, send response
            return JsonResponse({'message': 'You do not have any past trips'})

def getFriends(request):
    #Need access token to get friends - Make sure it isn't expired
    if 'fb_id' in request.session and 'access_token' in request.session:
        fb_id = int(request.session['fb_id'])
        trip = Trip.objects.get(id=request.session['current_trip'])
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
        trip = Trip.objects.get(id=request.session['current_trip'])
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

def updateItemPositions(request):
    items = request.POST.getlist('items[]', '0')
    for index in range(len(items)):
        items[index] = json.loads(items[index])
    print(items)
    if validateItems(request, items):
        for item in items:
            item_object = Item.objects.get(id=item['item_id'])
            item_object.day = Day.objects.get(id=item['day_id'])
            item_object.item_position = item['position']
            item_object.save()
        return HttpResponse("Items updated")
    else:
        return HttpResponse("Something went wrong")

def validateItems(request, items):
    current_trip = Trip.objects.get(id=request.session['current_trip'])
    for item in items:
        if Item.objects.get(id=item['item_id']).day.trip != current_trip:
            return False
    return True

def getYelpToken():
    yelp_token = cache.get('yelp_token')
    if not yelp_token:
        response = requests.post('https://api.yelp.com/oauth2/token?grant_type=client_credentials&client_secret=' + Ids.yelp_secret).json()
        yelp_token = response['access_token']
        timeout = 60*60*24*180
        cache.set('yelp_token', yelp_token, timeout)
    return yelp_token

def yelpTest(request):
    return render(request, 'yelpTest.html')

def getYelpResults(request):
    if request.method == 'GET':
        term = request.GET.get('term')
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        radius = request.GET.get('radius')
        yelp_token = getYelpToken()

        url = 'https://api.yelp.com/v3/businesses/search?term='+ term + '&latitude=' + latitude + '&longitude=' + longitude +'&radius=' + radius
        headers = {'Authorization': 'Bearer ' + yelp_token}
        response = requests.get(url, headers=headers)
        print(response.text)
        return response

def getFoursquareResults(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        # sw = request.GET.get('sw')
        # ne = request.GET.get('ne')
        # category = request.GET.get('category')
        ll = request.GET.get('ll')
        radius = request.GET.get('radius')
        page = request.GET.get('page')
        offset = (int(page) - 1) * 10

        url = 'https://api.foursquare.com/v2/venues/explore?client_id=' + Ids.foursquare_id + '&client_secret=' + Ids.foursquare_secret + '&v=20170702&m=foursquare&limit=10&offset=' + str(offset) + '&query=' + query + '&ll=' + ll + '&radius=' + radius + '&sortByDistance=0&time=any&day=any&venuePhotos=1'

        response = requests.get(url).json()
        print(response)
        complete_response = {}
        complete_response['venues'] = []
        for group in response['response']['groups']:
            for item in group['items']:
                complete_venue = requests.get('https://api.foursquare.com/v2/venues/' + item['venue']['id'] + '?client_id=' + Ids.foursquare_id + '&client_secret=' + Ids.foursquare_secret + '&v=20170702&m=foursquare').json()['response']['venue']
                #print(photo_response)
                complete_response['venues'].append(complete_venue)

        return JsonResponse(complete_response)

# This takes in a list of foursquare venue_id
def getFourSquareEvents(venueIdList):
    complete_response = {}
    complete_response['events'] = []
    for vid in venueIdList:
        complete_event = requests.get('https://api.foursquare.com/v2/venues/' + vid + '/events' + '?client_id=' + Ids.foursquare_id + '&client_secret=' + Ids.foursquare_secret)
        complete_response['events'].append(complete_event)
    return JsonResponse(complete_response)

def addItem(request):
    day_id = request.POST.get('day_id')
    day = Day.objects.get(id=day_id)
    permissions = request.session['trip_permission']
    if day.trip.id == request.session['current_trip'] and (permissions == "Creator" or permissions == "Can Edit"):
        highest_position = Item.objects.filter(day_id=day_id).order_by('-item_position')[:1]
        next_position = 1
        if highest_position:
            next_position = highest_position[0].item_position + 1

        item = Item.objects.create(item_name=request.POST.get('item_name'), item_position=next_position, day=day)

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
