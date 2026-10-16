import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import PrivateSalon, PrivateMenuPackage, EventService, PrivateEventInquiry

def private_dining_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        event_type = request.POST.get('event_type', 'private_dinner').strip()
        salon_id = request.POST.get('preferred_salon')
        date_str = request.POST.get('preferred_date', '').strip()
        time_slot = request.POST.get('preferred_time_slot', 'dinner').strip()
        guest_count_str = request.POST.get('guest_count', '12').strip()
        budget = request.POST.get('estimated_budget', '').strip()
        special_reqs = request.POST.get('special_requirements', '').strip()

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'

        if not full_name or not email or not phone or not date_str:
            error_msg = "Please provide all required fields (Full Name, Email, Telephone, and Preferred Date)."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('private_dining:private_dining_view')

        try:
            guests_num = int(guest_count_str)
            if guests_num < 1:
                guests_num = 1
        except ValueError:
            guests_num = 12

        try:
            preferred_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            error_msg = "Invalid date format provided."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('private_dining:private_dining_view')

        preferred_salon = None
        if salon_id:
            try:
                preferred_salon = PrivateSalon.objects.get(id=salon_id)
            except PrivateSalon.DoesNotExist:
                pass

        inquiry = PrivateEventInquiry.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            event_type=event_type,
            preferred_salon=preferred_salon,
            preferred_date=preferred_date,
            preferred_time_slot=time_slot,
            guest_count=guests_num,
            estimated_budget=budget,
            special_requirements=special_reqs,
            status='new',
        )

        salon_name = preferred_salon.name if preferred_salon else "Bespoke Salon"
        formatted_date = preferred_date.strftime("%A, %d %B %Y")
        success_msg = f"Inquiry registered! Reference: {inquiry.reference_id}. Our Events Director will prepare a customized proposal."

        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': success_msg,
                'reference_id': inquiry.reference_id,
                'full_name': inquiry.full_name,
                'date': formatted_date,
                'guests': inquiry.guest_count,
                'salon': salon_name,
            })

        messages.success(request, success_msg)
        return redirect('private_dining:private_dining_view')

    # GET Request
    salons = PrivateSalon.objects.filter(is_active=True)
    menus = PrivateMenuPackage.objects.all()
    services = EventService.objects.all()

    today_str = datetime.date.today().isoformat()
    max_date_str = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()

    context = {
        'salons': salons,
        'menus': menus,
        'services': services,
        'today_str': today_str,
        'max_date_str': max_date_str,
    }
    return render(request, 'private_dining/private_dining.html', context)
