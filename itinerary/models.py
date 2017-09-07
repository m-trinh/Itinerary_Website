from django.db import models

class User(models.Model):
    fb_id = models.BigIntegerField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

class Trip(models.Model):
    location = models.CharField(max_length=100)
    longitude = models.DecimalField(decimal_places=15, max_digits=18, null=True)
    latitude = models.DecimalField(decimal_places=15, max_digits=18, null=True)
    trip_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    create_date = models.DateTimeField(auto_now=True)
    can_edit = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)
    creator = models.ForeignKey(User)
    shared_users = models.ManyToManyField(User, related_name='shared_users')

    EVERYBODY = 'E'
    FRIENDS = 'F'
    SHARED = 'S'
    PUBLIC_LEVEL_CHOICES = (
        (EVERYBODY, 'Everybody'),
        (FRIENDS, 'Only Friends'),
        (SHARED, 'Only Friends That I Choose')
    )

    public_level = models.CharField(max_length=1, choices=PUBLIC_LEVEL_CHOICES, default=EVERYBODY)

    def __str__(self):
        return self.trip_name

class Day(models.Model):
    date = models.DateField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    day_start_address = models.CharField(max_length=100, null=True)
    day_start_longitude = models.DecimalField(decimal_places=15, max_digits=18, null=True)
    day_start_latitude = models.DecimalField(decimal_places=15, max_digits=18, null=True)

    def __str__(self):
        return str(self.date)

class Item(models.Model):
    fsq_id = models.CharField(max_length=50, null=True)
    item_name = models.CharField(max_length=100)
    item_position = models.PositiveIntegerField(null=True)
    item_description = models.CharField(max_length=1000, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    item_longitude = models.DecimalField(decimal_places=15, max_digits=18, null=True)
    item_latitude = models.DecimalField(decimal_places=15, max_digits=18, null=True)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, null=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=True)
    user_added = models.ForeignKey(User)

    def __str__(self):
        return self.item_name
