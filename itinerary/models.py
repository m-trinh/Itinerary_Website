from django.db import models

class Trip(models.Model):
    location = models.CharField(max_length=100)
    longitude = models.DecimalField(decimal_places=6, max_digits=10, null=True)
    latitude = models.DecimalField(decimal_places=6, max_digits=10, null=True)
    trip_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    create_date = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)
    #creator
    #shared_users

    def __str__(self):
        return self.trip_name

class Day(models.Model):
    date = models.DateField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date)

class Item(models.Model):
    item_name = models.CharField(max_length=100)
    item_position = models.PositiveIntegerField()
    item_description = models.CharField(max_length=1000, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    item_longitude = models.DecimalField(decimal_places=6, max_digits=10, null=True)
    item_latitude = models.DecimalField(decimal_places=6, max_digits=10, null=True)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    #adder_user

    def __str__(self):
        return self.item_name

    class Meta:
        unique_together = ('day', 'item_position')
    