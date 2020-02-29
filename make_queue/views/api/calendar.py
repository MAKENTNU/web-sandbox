from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from make_queue.models.models import Reservation


def reservation_type(reservation, user):
    if reservation.special:
        return "make"
    if reservation.event:
        return "event"
    if user is not None and reservation.user == user:
        return "own"
    return "normal"


def get_reservations(request, machine):
    start_date = parse_datetime(request.GET.get("startDate"))
    end_date = parse_datetime(request.GET.get("endDate"))
    reservations = []
    for reservation in Reservation.objects.filter(machine=machine, start_time__lt=end_date, end_time__gt=start_date):
        reservations.append({
            "start": reservation.start_time,
            "end": reservation.end_time,
            "type": reservation_type(reservation, request.user)
        })
    return JsonResponse({"reservations": reservations})
