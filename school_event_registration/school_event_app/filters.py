from django.utils import timezone


def filter_by_event_type(queryset, event_type):
    if event_type:
        return queryset.filter(event_type__name=event_type)
    return queryset


def filter_by_date(queryset, date_from, date_to):
    if date_from and date_to:
        if date_from <= date_to:
            return queryset.filter(date_and_time__range=[date_from, date_to])
    if date_from:
        return queryset.filter(date_and_time__gte=date_from)
    if date_to and date_to >= timezone.now().date().isoformat():
        return queryset.filter(date_and_time__lte=date_to)
    return queryset


def validate_dates(date_from, date_to):
    if date_from and date_to and date_from > date_to:
        return "The 'Date From' cannot be greater than the 'Date To'."
    if date_to and date_to < timezone.now().date().isoformat():
        return "The 'Date To' cannot be a past date."
    return None
