from rest_framework import serializers
from itinerary.models import Trip, Day, Item, User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('fb_id', 'email', 'first_name', 'last_name')

class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ('location', 'longitude', 'latitude', 'trip_name', 'description', 'start_date', 'end_date', 'create_date', 'public', 'can_edit', 'popularity')

class DaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Day
        fields = ('date', 'trip')

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        trip = validated_data['trip']
        session = self.context.get('request').session
        permissions = session['trip_permission']
        if trip.id == int(session['current_trip']) and (permissions == "Creator" or permissions == "Can Edit"):
            try:
                day = validated_data['day']
                print(day)
                if day.trip.id == trip.id:
                    #Find the highest item position in a day and put the new item above that
                    highest_position = Item.objects.filter(day_id=day.id).order_by('-item_position')[:1]
                    #If the day is empty, new item is in position 1
                    next_position = 1
                    if highest_position:
                        next_position = highest_position[0].item_position + 1
                    validated_data['item_position'] = next_position
            except KeyError:
                pass
            user_added = User.objects.get(fb_id=session['fb_id'])
            validated_data['user_added'] = user_added
            #Once new item has a position, create the object in database
            item = Item.objects.create(**validated_data)
            return item

    class Meta:
        model = Item
        fields = ('id', 'fsq_id', 'item_name', 'item_description', 'start_time', 'end_time', 'item_longitude', 'item_latitude', 'day', 'trip')