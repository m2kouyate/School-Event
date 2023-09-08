from django import forms
from .models import Event, EventType, Participant, EventImage
from django.utils import timezone


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name', 'description']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date_and_time', 'location', 'description', 'max_participants', 'event_type']
        widgets = {
            'date_and_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'min': timezone.now().strftime('%Y-%m-%dT%H:%M')}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if user:
            self.instance.created_by = user


class EventImageForm(forms.ModelForm):
    image = MultipleFileField(label='Image files', required=False)

    class Meta:
        model = EventImage
        fields = ['image']


EventImageFormSet = forms.inlineformset_factory(
    Event, EventImage, form=EventImageForm, extra=1, can_delete=False
)


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['first_name', 'last_name', 'profile_picture', 'email', 'phone_number']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class EventImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV file', required=True)
    image_files = MultipleFileField(label='Image files', required=False)
    event_type = forms.ModelChoiceField(queryset=EventType.objects.all(), required=False)






