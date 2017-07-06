from django import forms

class CreateTripForm(forms.Form):
    location = forms.CharField(label="Location", max_length=100)
    longitude = forms.DecimalField(widget=forms.HiddenInput())
    latitude = forms.DecimalField(widget=forms.HiddenInput())
    trip_name = forms.CharField(label="Trip Name", max_length=100, required=False)
    description = forms.CharField(label="Trip Description", widget=forms.Textarea, max_length=1000, required=False)
    start_date = forms.DateField(label="Start Date", widget=forms.DateInput)
    end_date = forms.DateField(label="End Date", widget=forms.DateInput)

    EVERYBODY = 'E'
    FRIENDS = 'F'
    SHARED = 'S'
    PUBLIC_LEVEL_CHOICES = (
        (EVERYBODY, 'Everybody'),
        (FRIENDS, 'Only Friends'),
        (SHARED, 'Only Friends That I Choose')
    )

    public = forms.CharField(label="Public Level", max_length=1, widget=forms.Select(choices=PUBLIC_LEVEL_CHOICES))