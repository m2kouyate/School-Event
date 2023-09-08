from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin

from .filters import filter_by_event_type, filter_by_date, validate_dates
from .models import Event, EventType, Participant, EventImage
from .forms import EventForm, EventTypeForm, ParticipantForm, EventImportForm, EventImageFormSet


from .service_views import EventImageFormMixin, get_event_update_forms, handle_event_update_post, check_event_owner, \
    superuser_required, get_participant_initial_data, check_and_save_participant, handle_uploaded_files, \
    create_event_and_images_from_row, clean_up_temp_dir


class EventListView(ListView):
    model = Event
    template_name = 'school_event/event_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        event_type = self.request.GET.get('event_type')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        queryset = filter_by_event_type(queryset, event_type)
        queryset = filter_by_date(queryset, date_from, date_to)

        return queryset.order_by('date_and_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = EventType.objects.all()

        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        date_error = validate_dates(date_from, date_to)
        if date_error:
            context['date_error'] = date_error

        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'school_event/event_detail.html'

    def get_queryset(self):
        return super().get_queryset().select_related('event_type', 'created_by').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['participants'] = Participant.objects.filter(event=event).select_related('user')
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'school_event/event_form.html'

    mixin = EventImageFormMixin()

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_form = EventImageFormSet(queryset=EventImage.objects.none())
        return self.render_to_response(
            self.get_context_data(form=form, image_form=image_form)
        )

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_form = EventImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            return self.form_valid(form, image_form)
        else:
            return self.form_invalid(form, image_form)

    @transaction.atomic
    def form_valid(self, form, image_form):
        form.instance.created_by = self.request.user
        self.object = form.save()
        self.mixin.handle_image_form(self.object, image_form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('school_event_app:event_list')


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'school_event/event_form.html'

    mixin = EventImageFormMixin()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form, image_form = get_event_update_forms(request, form_class, self.object)
        return self.render_to_response(
            self.get_context_data(form=form, image_form=image_form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form, image_form = handle_event_update_post(request, form_class, self.object)
        if form.is_valid() and image_form.is_valid():
            return self.form_valid(form, image_form)
        else:
            return self.form_invalid(form, image_form)

    @transaction.atomic
    def form_valid(self, form, image_form):
        self.object = form.save()
        self.mixin.handle_image_form(self.object, image_form)
        return HttpResponseRedirect(self.get_success_url())

    def test_func(self):
        obj = self.get_object()
        return check_event_owner(obj, self.request.user)

    def get_success_url(self):
        return reverse_lazy('school_event_app:event_list')


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'school_event/event_confirm_delete.html'
    success_url = reverse_lazy('school_event_app:event_list')
    _object = None

    def get_object(self, queryset=None):
        if not self._object:
            self._object = super().get_object(queryset)
        return self._object

    def test_func(self):
        obj = self.get_object()
        return check_event_owner(obj, self.request.user)


class EventTypeCreateView(LoginRequiredMixin, CreateView):
    model = EventType
    form_class = EventTypeForm
    template_name = 'school_event/eventtype_form.html'
    success_url = reverse_lazy('school_event_app:event_list')

    @superuser_required
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
        except ObjectDoesNotExist:
            messages.error(self.request, "EventType not found")
            return redirect('school_event_app:event_type_list')
        return obj


class EventTypeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = EventType
    form_class = EventTypeForm
    template_name = 'school_event/eventtype_form.html'
    success_url = reverse_lazy('school_event_app:event_type_list')

    def has_permission(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
        except ObjectDoesNotExist:
            messages.error(self.request, "EventType not found")
            return redirect('school_event_app:event_type_list')
        return obj

    def get_success_url(self):
        return reverse_lazy('school_event_app:event_list')


class EventTypeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = EventType
    template_name = 'school_event/eventtype_confirm_delete.html'
    success_url = reverse_lazy('school_event_app:event_type_list')

    def has_permission(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
        except ObjectDoesNotExist:
            messages.error(self.request, "EventType not found")
            return redirect('school_event_app:event_type_list')
        return obj

    def get_success_url(self):
        return reverse_lazy('school_event_app:event_list')


class EventTypeDetailView(DetailView):
    model = EventType
    template_name = 'school_event/eventtype_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(event_type=self.object).select_related('created_by')
        return context


class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'school_event/participant_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial.update(get_participant_initial_data(self.request))
        return initial

    def form_valid(self, form):
        form, participant = check_and_save_participant(form, self.request, self.kwargs['event_pk'])
        if participant:
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('school_event_app:event_detail', kwargs={'pk': self.kwargs['event_pk']})


class EventImportView(LoginRequiredMixin, FormView):
    template_name = 'school_event/event_import.html'
    form_class = EventImportForm

    @transaction.atomic
    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        image_files = form.cleaned_data['image_files']
        event_type = form.cleaned_data['event_type']

        reader, image_paths = handle_uploaded_files(csv_file, image_files)

        events_to_create = []
        images_to_create = []
        for row in reader:
            event_list, image_list = create_event_and_images_from_row(row, event_type, self.request, image_paths)
            events_to_create.extend(event_list)
            images_to_create.extend(image_list)

        Event.objects.bulk_create(events_to_create)
        EventImage.objects.bulk_create(images_to_create)

        clean_up_temp_dir('media/event_images/temp/')

        return redirect('school_event_app:event_list')

    def form_invalid(self, form):
        messages.error(self.request, "Error importing events")
        return self.render_to_response(self.get_context_data(form=form))



