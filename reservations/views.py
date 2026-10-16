import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import SeatingArea, DiningExperience, ReservationPolicy, TableReservation

def reservations_view(request):
    if request.method == 'POST':
        guest_name = request.POST.get('guest_name', '').strip()
        guest_email = request.POST.get('guest_email', '').strip()
        guest_phone = request.POST.get('guest_phone', '').strip()
        guests_count = request.POST.get('guests_count', '2').strip()
        reservation_date_str = request.POST.get('reservation_date', '').strip()
        reservation_time = request.POST.get('reservation_time', '').strip()
        seating_area_id = request.POST.get('seating_area')
        dining_experience = request.POST.get('dining_experience', 'A La Carte Experience').strip()
        occasion = request.POST.get('occasion', 'casual').strip()
        dietary_requests = request.POST.get('dietary_requests', '').strip()
        special_requests = request.POST.get('special_requests', '').strip()
        
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'

        # Validation
        if not guest_name or not guest_email or not guest_phone or not reservation_date_str or not reservation_time:
            error_msg = "Please provide all required fields (Name, Email, Telephone, Date, and Time)."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('reservations:reservations_view')

        try:
            guests_num = int(guests_count)
            if guests_num < 1:
                guests_num = 1
        except ValueError:
            guests_num = 2

        try:
            reservation_date = datetime.date.fromisoformat(reservation_date_str)
        except ValueError:
            error_msg = "Invalid reservation date provided."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('reservations:reservations_view')

        seating_area = None
        if seating_area_id:
            try:
                seating_area = SeatingArea.objects.get(id=seating_area_id)
            except SeatingArea.DoesNotExist:
                pass

        # Create Table Reservation
        reservation = TableReservation.objects.create(
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            guests_count=guests_num,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            seating_area=seating_area,
            dining_experience=dining_experience,
            occasion=occasion,
            dietary_requests=dietary_requests,
            special_requests=special_requests,
            status='confirmed',
        )

        area_display = seating_area.name if seating_area else "Main Dining Room"
        formatted_date = reservation_date.strftime("%A, %d %B %Y")
        
        success_msg = f"Your table has been reserved! Booking Reference: {reservation.booking_reference}. We look forward to welcoming you."

        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': success_msg,
                'booking_reference': reservation.booking_reference,
                'guest_name': reservation.guest_name,
                'date': formatted_date,
                'time': reservation.reservation_time,
                'guests': reservation.guests_count,
                'area': area_display,
            })

        messages.success(request, success_msg)
        return redirect('reservations:reservations_view')

    # GET Request
    seating_areas = SeatingArea.objects.filter(is_active=True)
    experiences = DiningExperience.objects.all()
    policy = ReservationPolicy.objects.first()

    today_str = datetime.date.today().isoformat()
    max_date_str = (datetime.date.today() + datetime.timedelta(days=60)).isoformat()

    lunch_slots = ['12:00', '12:30', '13:00', '13:30', '14:00', '14:30']
    dinner_slots = ['17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30']

    context = {
        'seating_areas': seating_areas,
        'experiences': experiences,
        'policy': policy,
        'today_str': today_str,
        'max_date_str': max_date_str,
        'lunch_slots': lunch_slots,
        'dinner_slots': dinner_slots,
    }
    return render(request, 'reservations/reservations.html', context)
