import csv
import io
import os
import shutil
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from .forms import EventImageFormSet
from .models import EventImage, Participant, Event


class EventImageFormMixin:
    def handle_image_form(self, object, image_form):
        image_form.instance = object

        new_images = []

        for img_form in image_form:
            if img_form.cleaned_data:
                if img_form.cleaned_data.get('DELETE'):
                    img_form.instance.delete()
                else:
                    images = img_form.cleaned_data.get('image')
                    if images:
                        if isinstance(images, list):
                            for image in images:
                                new_images.append(EventImage(event=object, image=image))
                        else:
                            new_images.append(EventImage(event=object, image=images))

        EventImage.objects.bulk_create(new_images)

    def form_invalid(self, form, image_form):
        return self.render_to_response(
            self.get_context_data(form=form, image_form=image_form)
        )


def get_event_update_forms(request, form_class, object):
    form = form_class(instance=object)
    form.instance.created_by = request.user
    image_form = EventImageFormSet(queryset=EventImage.objects.filter(event=object))
    return form, image_form


def handle_event_update_post(request, form_class, object):
    form = form_class(request.POST, instance=object)
    image_form = EventImageFormSet(request.POST, request.FILES, queryset=EventImage.objects.filter(event=object))
    return form, image_form


def check_event_owner(object, user):
    return object.created_by == user


def superuser_required(func):
    def wrapper(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create event types")
        return func(self, *args, **kwargs)
    return wrapper


def get_participant_initial_data(request):
    initial = {}
    if request.user.is_authenticated:
        initial.update({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
        if hasattr(request.user, 'profile') and request.user.profile.profile_picture:
            initial['profile_picture'] = request.user.profile.profile_picture
    return initial


def check_and_save_participant(form, request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    participant = form.save(commit=False)

    participant_count = event.participant_set.count()
    if participant_count >= event.max_participants or \
       Participant.objects.filter(email=participant.email, event=event).exists():
        if participant_count >= event.max_participants:
            return HttpResponseForbidden("The maximum number of participants has been reached for this event.")
        form.add_error('email', 'A participant with this email is already registered for this event.')
        return form, None

    participant.event = event

    if request.user.is_authenticated:
        participant.user = request.user
    else:
        if not participant.first_name or not participant.last_name:
            form.add_error(None, "First name and last name are required for unregistered users")
            return form, None

    participant.save()
    messages.success(request, "You have successfully registered for the event!")
    return form, participant


def handle_uploaded_files(csv_file, image_files):
    decoded_file = csv_file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.reader(io_string, delimiter=',', quotechar="|")

    temp_dir = 'media/event_images/temp/'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    image_paths = {}
    for image_file in image_files:
        temp_file_path = os.path.join(temp_dir, image_file.name)
        with open(temp_file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        image_paths[image_file.name] = temp_file_path

    return reader, image_paths


def create_event_and_images_from_row(row, event_type, request, image_paths):
    events_to_create = []
    images_to_create = []

    if len(row) < 6:
        messages.error(request, f"Row is missing fields: {row}")
        return events_to_create, images_to_create

    name, date_and_time_str, location, description, max_participants_str, image_filenames_str = row

    date_and_time_obj = parse_datetime(date_and_time_str)
    if not date_and_time_obj:
        messages.error(request, f"Invalid date format for event: {name}")
        return events_to_create, images_to_create

    try:
        max_participants = int(max_participants_str)
    except ValueError:
        messages.error(request, f"Invalid max participants value for event: {name}")
        return events_to_create, images_to_create

    event = Event(
        name=name,
        date_and_time=date_and_time_obj,
        location=location,
        description=description,
        max_participants=max_participants,
        event_type=event_type,
        created_by=request.user
    )
    events_to_create.append(event)

    event_images_folder_path = f'media/event_images/{event.name}/'
    if not os.path.exists(event_images_folder_path):
        os.makedirs(event_images_folder_path)

    image_filenames = image_filenames_str.split(';')
    not_found_images = []
    for image_filename in image_filenames:
        if image_filename in image_paths:
            temp_image_path = image_paths[image_filename]
            new_image_path = os.path.join(event_images_folder_path, image_filename)
            shutil.move(temp_image_path, new_image_path)
            images_to_create.append(EventImage(event=event, image=new_image_path[len('media/'):]))
        else:
            not_found_images.append(image_filename)

    if not_found_images:
        messages.error(request,
                       f"Events imported but could not find images: {', '.join(not_found_images)} for event: {event.name}")
    else:
        messages.success(request, f"Events imported successfully for event: {event.name}")

    return events_to_create, images_to_create


def clean_up_temp_dir(temp_dir):
    shutil.rmtree(temp_dir)

