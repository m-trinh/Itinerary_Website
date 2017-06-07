from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from itinerary.models import Trip, Day, Item
from itinerary.views.forms import CreateTripForm
from datetime import timedelta, date
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from django.views.decorators.csrf import ensure_csrf_cookie
from itinerary.views.serializers import TripSerializer, DaySerializer, ItemSerializer
from django.db.models import Max

def index(request):
    return render(request, 'home.html')
    
def createTrip(request):
    #TODO: Refactor this using the serializers
    if request.method == 'POST':
        form = CreateTripForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            trip_name = form.cleaned_data['trip_name']
            description = form.cleaned_data['description']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if not trip_name:
                trip_name = location

            trip = Trip(location=location, trip_name=trip_name, description=description, start_date=start_date, end_date=end_date)
            trip.save()

            trip_duration = (end_date - start_date).days
            increment = timedelta(days=1)
            current_day = start_date
            day = Day(date=current_day, trip=trip)
            day.save()

            for num in range(0, trip_duration):
                current_day = current_day + increment
                day = Day(date=current_day, trip=trip)
                day.save()

            return redirect('showTrip', tripID=trip.id)

    else:
        form = CreateTripForm()
        return render(request, 'createTrip.html', {'form': form})

def showAllTrips(request):
    trips = Trip.objects.all()
    return render(request, 'allTrips.html', {'trips': trips})


@ensure_csrf_cookie
def showTrip(request, tripID):
    #TODO: When users are set up, check for the permissions

    #Find trip from id and display its days and items
    trip = Trip.objects.get(id=tripID)
    days = Day.objects.filter(trip_id=tripID).order_by('date')
    for day in days:
        items = Item.objects.filter(day_id=day.id)
        day.items = items
    return render(request, 'showTrip.html', {'trip': trip, 'days': days})


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

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    