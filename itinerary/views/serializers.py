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
        day_id = validated_data['day'].id

        #Find the highest item position in a day and put the new item above that
        highest_position = Item.objects.filter(day_id=day_id).order_by('-item_position')[:1]
        user_added = self.context.get('request').fb_id
        #If the day is empty, new item is in position 1
        next_position = 1
        if highest_position:
            next_position = highest_position[0].item_position + 1
        validated_data['item_position'] = next_position
        validated_data['user_added'] = user_added
        #Once new item has a position, create the object in database
        item = Item.objects.create(**validated_data)
        return item

    class Meta:
        model = Item
        fields = ('item_name', 'item_description', 'start_time', 'end_time', 'item_longitude', 'item_latitude', 'day')