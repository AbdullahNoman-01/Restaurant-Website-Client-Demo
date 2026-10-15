from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import ContactInfo, ContactDepartment, ContactFAQ, ContactMessage

def contact_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        inquiry_type = request.POST.get('inquiry_type', 'general')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'

        if not full_name or not email or not message:
            error_msg = "Please fill in all required fields (Name, Email, and Message)."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        else:
            if not subject:
                subject = f"{dict(ContactMessage.INQUIRY_CHOICES).get(inquiry_type, 'General Inquiry')} from {full_name}"

            ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                inquiry_type=inquiry_type,
                subject=subject,
                message=message,
            )

            success_msg = "Thank you for contacting The Chesterfield. Our guest relations brigade will review your inquiry and reply within 24 hours."
            if is_ajax:
                return JsonResponse({'status': 'success', 'message': success_msg})
            messages.success(request, success_msg)
            return redirect('contact:contact_view')

    info = ContactInfo.objects.first()
    departments = ContactDepartment.objects.all()
    faqs = ContactFAQ.objects.all()

    context = {
        'info': info,
        'departments': departments,
        'faqs': faqs,
    }
    return render(request, 'contact/contact.html', context)
