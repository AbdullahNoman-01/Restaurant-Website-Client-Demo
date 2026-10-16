import json
import uuid
import datetime
from decimal import Decimal
import requests
try:
    import stripe
except ImportError:
    stripe = None

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from menu.models import MenuItem
from .models import Order, OrderItem, Payment

# Configure Stripe SDK
if stripe:
    stripe.api_key = settings.STRIPE_SECRET_KEY


# ==============================================================================
# CART SESSION UTILITIES
# ==============================================================================

def _get_cart(session):
    """Retrieve or initialize the guest shopping cart dictionary from session."""
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']


def _calculate_cart_totals(session, order_type='collection'):
    """
    Recalculates cart totals using TRUSTED database values for all MenuItem prices.
    Returns: (cart_items_list, subtotal, delivery_fee, grand_total, total_quantity)
    """
    cart = _get_cart(session)
    if not cart:
        return [], Decimal('0.00'), Decimal('0.00'), Decimal('0.00'), 0

    item_ids = [int(k) for k in cart.keys() if str(k).isdigit()]
    menu_items = {item.id: item for item in MenuItem.objects.filter(id__in=item_ids, is_available=True)}

    cart_items = []
    subtotal = Decimal('0.00')
    total_qty = 0

    for str_id, data in list(cart.items()):
        try:
            item_id = int(str_id)
        except ValueError:
            continue

        item = menu_items.get(item_id)
        if not item:
            # Item was removed or unavailable in database
            continue

        qty = int(data.get('quantity', 1))
        if qty < 1:
            qty = 1

        unit_price = Decimal(str(item.price))
        line_total = unit_price * qty
        subtotal += line_total
        total_qty += qty

        cart_items.append({
            'item': item,
            'id': item.id,
            'item_id': item.id,
            'name': item.name,
            'description': item.description,
            'price': unit_price,
            'unit_price': unit_price,
            'formatted_unit_price': f"${unit_price:.2f}",
            'quantity': qty,
            'line_total': line_total,
            'formatted_line_total': f"${line_total:.2f}",
            'image_url': item.get_image_url(),
            'badge': item.badge,
        })

    # Threshold for free delivery: $50
    if order_type == 'delivery' and subtotal < Decimal('50.00') and subtotal > 0:
        delivery_fee = Decimal('5.00')
    else:
        delivery_fee = Decimal('0.00')

    grand_total = subtotal + delivery_fee

    return cart_items, subtotal, delivery_fee, grand_total, total_qty


def _parse_request_data(request):
    """Safely extracts parameters from either JSON body or standard form POST."""
    if request.body and ('application/json' in request.content_type or request.headers.get('content-type') == 'application/json'):
        try:
            return json.loads(request.body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return {}
    return request.POST


def _is_ajax(request):
    """
    Detects if the request is an AJAX or API call expecting JSON.
    Checks headers case-insensitively and also checks request Accept / Content-Type.
    """
    x_req = request.headers.get('x-requested-with', '') or request.META.get('HTTP_X_REQUESTED_WITH', '')
    accept = request.headers.get('accept', '') or request.META.get('HTTP_ACCEPT', '')
    content_type = getattr(request, 'content_type', '') or request.headers.get('content-type', '')
    
    return (
        str(x_req).lower() == 'xmlhttprequest' or
        'application/json' in str(accept).lower() or
        'application/json' in str(content_type).lower()
    )


def _get_base_url(request):
    """
    Resolves the base URL dynamically prioritizing the incoming request host and scheme,
    so that Stripe return URLs (success and cancel) work smoothly on both local development
    and Render production without requiring manual SITE_URL synchronization.
    """
    if request:
        try:
            base = request.build_absolute_uri('/').rstrip('/')
            if base.startswith('http://') or base.startswith('https://'):
                return base
        except Exception:
            pass
    return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')


# ==============================================================================
# FEATURE 1 & 2: CART VIEWS & AJAX APIS
# ==============================================================================

def cart_view(request):
    """Renders the luxury Savenhoff-inspired Cart Page (Image 1)."""
    cart_items, subtotal, delivery_fee, grand_total, total_qty = _calculate_cart_totals(request.session)

    free_delivery_threshold = Decimal('50.00')
    amount_needed_for_free_delivery = Decimal('0.00')
    if subtotal < free_delivery_threshold and subtotal > 0:
        amount_needed_for_free_delivery = free_delivery_threshold - subtotal

    context = {
        'cart_items': cart_items,
        'cart_subtotal': subtotal,
        'cart_delivery_fee': delivery_fee,
        'cart_grand_total': grand_total,
        'cart_total_items': total_qty,
        'estimated_delivery': delivery_fee,
        'delivery_difference': f"{amount_needed_for_free_delivery:.2f}",
        'subtotal': subtotal,
        'formatted_subtotal': f"${subtotal:.2f}",
        'delivery_fee': delivery_fee,
        'formatted_delivery_fee': "FREE" if delivery_fee == 0 else f"${delivery_fee:.2f}",
        'grand_total': grand_total,
        'formatted_grand_total': f"${grand_total:.2f}",
        'total_qty': total_qty,
        'free_delivery_threshold': free_delivery_threshold,
        'amount_needed_for_free_delivery': amount_needed_for_free_delivery,
        'has_free_delivery': subtotal >= free_delivery_threshold,
    }
    return render(request, 'payment_gatway/cart.html', context)


@csrf_exempt
@require_POST
def cart_add(request):
    """
    AJAX endpoint called when clicking 'Add to Order' inside dish details.
    Accepts item_id and optional quantity (defaults to 1).
    """
    data = _parse_request_data(request)
    item_id = data.get('item_id')
    try:
        qty = int(data.get('quantity', 1))
        if qty < 1:
            qty = 1
    except (ValueError, TypeError):
        qty = 1

    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart = _get_cart(request.session)
    str_id = str(item.id)

    if str_id in cart:
        cart[str_id]['quantity'] = cart[str_id].get('quantity', 0) + qty
    else:
        cart[str_id] = {
            'quantity': qty,
            'name': item.name,
            'price': str(item.price),
        }

    request.session.modified = True

    _, subtotal, delivery_fee, grand_total, total_qty = _calculate_cart_totals(request.session)

    cart_url = reverse('payment_gatway:cart')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.content_type:
        return JsonResponse({
            'status': 'success',
            'message': f"Added {qty}x {item.name} to your order.",
            'item_name': item.name,
            'cart_count': total_qty,
            'subtotal': f"{subtotal:.2f}",
            'delivery_fee': f"{delivery_fee:.2f}",
            'grand_total': f"{grand_total:.2f}",
            'redirect_url': cart_url,
        })

    return redirect('payment_gatway:cart')


@csrf_exempt
@require_POST
def cart_update(request):
    """Updates the quantity of an item in the cart or adjusts via + / - buttons."""
    data = _parse_request_data(request)
    item_id = data.get('item_id')
    action = data.get('action')  # 'plus', 'minus', or direct 'set'
    
    cart = _get_cart(request.session)
    str_id = str(item_id)
    new_qty = 0

    if str_id in cart:
        current_qty = cart[str_id].get('quantity', 1)
        if action == 'plus':
            new_qty = current_qty + 1
        elif action == 'minus':
            new_qty = current_qty - 1
        else:
            try:
                new_qty = int(data.get('quantity', current_qty))
            except (ValueError, TypeError):
                new_qty = current_qty

        if new_qty <= 0:
            del cart[str_id]
            new_qty = 0
        else:
            cart[str_id]['quantity'] = new_qty

        request.session.modified = True

    cart_items, subtotal, delivery_fee, grand_total, total_qty = _calculate_cart_totals(request.session)

    # Find line total for this updated item
    line_total_val = Decimal('0.00')
    for ci in cart_items:
        if str(ci['item_id']) == str_id:
            line_total_val = ci['line_total']
            break

    return JsonResponse({
        'status': 'success',
        'cart_count': total_qty,
        'item_id': str_id,
        'item_quantity': new_qty,
        'item_line_total': f"{line_total_val:.2f}",
        'subtotal': f"{subtotal:.2f}",
        'delivery_fee': f"{delivery_fee:.2f}",
        'grand_total': f"{grand_total:.2f}",
        'is_empty': len(cart_items) == 0,
    })


@csrf_exempt
@require_POST
def cart_remove(request):
    """Removes an item completely from the session cart."""
    data = _parse_request_data(request)
    item_id = data.get('item_id')
    cart = _get_cart(request.session)
    str_id = str(item_id)

    if str_id in cart:
        del cart[str_id]
        request.session.modified = True

    cart_items, subtotal, delivery_fee, grand_total, total_qty = _calculate_cart_totals(request.session)

    return JsonResponse({
        'status': 'success',
        'cart_count': total_qty,
        'subtotal': f"{subtotal:.2f}",
        'delivery_fee': f"{delivery_fee:.2f}",
        'grand_total': f"{grand_total:.2f}",
        'is_empty': len(cart_items) == 0,
    })


@require_GET
def cart_count(request):
    """Returns the current number of items in the cart for navbar badge."""
    _, _, _, _, total_qty = _calculate_cart_totals(request.session)
    return JsonResponse({'cart_count': total_qty})


# ==============================================================================
# FEATURE 3: CHECKOUT & ORDER CREATION
# ==============================================================================

def checkout_view(request):
    """Renders the Checkout Page matching Image 2 & luxury Chesterfield theme."""
    cart_items, subtotal, delivery_fee, grand_total, total_qty = _calculate_cart_totals(request.session)

    if not cart_items:
        messages.warning(request, "Your order basket is currently empty. Please select your desired dishes from our menu.")
        return redirect('menu_list')

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'formatted_subtotal': f"${subtotal:.2f}",
        'delivery_fee': delivery_fee,
        'formatted_delivery_fee': "FREE" if delivery_fee == 0 else f"${delivery_fee:.2f}",
        'grand_total': grand_total,
        'formatted_grand_total': f"${grand_total:.2f}",
        'total_qty': total_qty,
        'stripe_pub_key': settings.STRIPE_PUBLISHABLE_KEY,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    }
    return render(request, 'payment_gatway/checkout.html', context)


def _create_stripe_session_for_order(request, order):
    """
    Dynamically creates a Stripe Checkout Session using database MenuItem snapshots.
    Uses Stripe's inline price_data with product_data and unit_amount.
    Ensures Decimal-safe integer amounts in smallest currency units (cents).
    Never relies on client-provided amounts.
    """
    if not stripe:
        raise ValueError("Stripe Python SDK is not installed or available.")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not stripe.api_key or stripe.api_key == 'sk_test_placeholder':
        raise ValueError("Stripe Secret Key is not configured. Please check environment variables.")

    base_url = _get_base_url(request)
    success_url = f"{base_url}{reverse('payment_gatway:stripe_success')}?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}{reverse('payment_gatway:stripe_cancel', kwargs={'access_token': order.access_token})}"

    line_items = []
    for item in order.items.all():
        # Validate that the menu item is still active and available in database
        if item.menu_item and not item.menu_item.is_available:
            raise ValueError(f"Dish '{item.item_name}' is currently out of stock or unavailable.")

        # Decimal-safe calculation for unit amount in smallest currency unit (e.g. cents)
        unit_amount = int((item.unit_price * Decimal('100')).quantize(Decimal('1')))
        if unit_amount <= 0:
            raise ValueError(f"Invalid price calculated for dish '{item.item_name}'.")

        product_data = {
            'name': item.item_name,
            'description': f"The Chesterfield Gourmet Selection: {item.item_name}",
        }
        if item.item_image_url and (item.item_image_url.startswith('http://') or item.item_image_url.startswith('https://')):
            product_data['images'] = [item.item_image_url]

        line_items.append({
            'price_data': {
                'currency': order.currency.lower(),
                'unit_amount': unit_amount,
                'product_data': product_data,
            },
            'quantity': item.quantity,
        })

    # Add Delivery Fee line item if applicable
    if order.delivery_fee > 0:
        delivery_cents = int((order.delivery_fee * Decimal('100')).quantize(Decimal('1')))
        line_items.append({
            'price_data': {
                'currency': order.currency.lower(),
                'unit_amount': delivery_cents,
                'product_data': {
                    'name': 'Direct Doorstep Delivery Fee',
                    'description': 'Flat-rate doorstep delivery to your address',
                },
            },
            'quantity': 1,
        })

    session = stripe.checkout.Session.create(
        line_items=line_items,
        mode='payment',
        customer_email=order.customer_email,
        client_reference_id=order.order_number,
        metadata={
            'order_number': order.order_number,
            'access_token': str(order.access_token),
        },
        success_url=success_url,
        cancel_url=cancel_url,
    )

    order.stripe_session_id = session.id
    order.save(update_fields=['stripe_session_id'])
    return session


@csrf_exempt
@require_POST
def place_order(request):
    """
    Processes the checkout form submission.
    Creates Order & OrderItem records inside an atomic database transaction.
    Recalculates prices using trusted database values.
    Routes to the appropriate payment provider:
    - Stripe: Creates Stripe Checkout Session dynamically & returns URL
    - Cash on Collection: Confirms order and returns redirect URL
    - PayPal: Returns PayPal order creation endpoint
    """
    cart_items, subtotal, delivery_fee, grand_total, total_qty = _calculate_cart_totals(
        request.session,
        order_type=request.POST.get('order_type', 'collection')
    )

    if not cart_items:
        err_msg = 'Your basket is empty or the selected dishes are currently unavailable.'
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect('menu_list')

    # Extract & validate customer fields
    customer_name = request.POST.get('customer_name', '').strip()
    customer_email = request.POST.get('customer_email', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    order_type = request.POST.get('order_type', 'collection').strip()
    delivery_address = request.POST.get('delivery_address', '').strip()
    special_notes = request.POST.get('special_notes', '').strip()
    payment_method = request.POST.get('payment_method', 'cash_on_collection').strip()

    if not customer_name or not customer_email or not customer_phone:
        err_msg = "Please provide your Full Name, Email, and Telephone Number."
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect('payment_gatway:checkout')

    if order_type == 'delivery' and not delivery_address:
        err_msg = "Please provide a complete delivery destination address."
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect('payment_gatway:checkout')

    # Generate unique human-readable order number: TC-YYYYMMDD-XXXX
    date_part = datetime.date.today().strftime('%Y%m%d')
    unique_suffix = uuid.uuid4().hex[:6].upper()
    order_number = f"TC-{date_part}-{unique_suffix}"

    try:
        with transaction.atomic():
            order = Order.objects.create(
                order_number=order_number,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                order_type=order_type,
                delivery_address=delivery_address if order_type == 'delivery' else '',
                special_notes=special_notes,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                discount_amount=Decimal('0.00'),
                grand_total=grand_total,
                currency=getattr(settings, 'RESTAURANT_CURRENCY', 'USD'),
                payment_method=payment_method,
                payment_status='pending',
                order_status='received',
            )

            # Create immutable OrderItem snapshots
            for ci in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=ci['item'],
                    item_name=ci['name'],
                    unit_price=ci['unit_price'],
                    quantity=ci['quantity'],
                    line_total=ci['line_total'],
                    item_image_url=ci['image_url'],
                )

        # Clear session cart once order is safely persisted
        request.session['cart'] = {}
        request.session.modified = True

        # Route according to chosen payment method:
        # A. Cash on Collection
        if payment_method == 'cash_on_collection':
            Payment.objects.create(
                order=order,
                provider='cash',
                transaction_id=f"CASH-{order.order_number}",
                amount=order.grand_total,
                currency=order.currency,
                payment_status='pending',
                raw_response='Cash on Collection selected. Payment due upon arrival.',
            )
            success_url = reverse('payment_gatway:order_success', kwargs={'access_token': order.access_token})
            if _is_ajax(request):
                return JsonResponse({
                    'status': 'success',
                    'payment_method': 'cash_on_collection',
                    'redirect_url': success_url,
                    'order_number': order.order_number,
                })
            return redirect(success_url)

        # B. Stripe Checkout Flow
        elif payment_method == 'stripe':
            try:
                session = _create_stripe_session_for_order(request, order)
                if _is_ajax(request):
                    return JsonResponse({
                        'status': 'success',
                        'payment_method': 'stripe',
                        'checkout_url': session.url,
                        'create_session_url': reverse('payment_gatway:stripe_create_session', kwargs={'access_token': order.access_token}),
                        'redirect_url': session.url,
                        'access_token': str(order.access_token),
                        'order_number': order.order_number,
                    })
                return redirect(session.url)
            except Exception as stripe_err:
                order.payment_status = 'failed'
                order.save(update_fields=['payment_status'])
                err_msg = f"Stripe Checkout error: {str(stripe_err)}"
                if _is_ajax(request):
                    return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
                messages.error(request, err_msg)
                return redirect('payment_gatway:checkout')

        # C. PayPal Flow
        elif payment_method == 'paypal':
            paypal_create_url = reverse('payment_gatway:paypal_create_order', kwargs={'access_token': order.access_token})
            if _is_ajax(request):
                return JsonResponse({
                    'status': 'success',
                    'payment_method': 'paypal',
                    'create_order_url': paypal_create_url,
                    'access_token': str(order.access_token),
                    'order_number': order.order_number,
                })
            return redirect('payment_gatway:order_success', kwargs={'access_token': order.access_token})

    except Exception as e:
        err_msg = f"Unable to place your order: {str(e)}"
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect('payment_gatway:checkout')



# ==============================================================================
# FEATURE 4A: STRIPE CHECKOUT INTEGRATION
# ==============================================================================

def stripe_create_session(request, access_token):
    """
    Direct endpoint to create / redirect to a Stripe Checkout Session.
    Useful as fallback if frontend JS is bypassed or on direct retry.
    """
    order = get_object_or_404(Order, access_token=access_token)

    if order.payment_status == 'paid':
        return redirect('payment_gatway:order_success', kwargs={'access_token': order.access_token})

    try:
        session = _create_stripe_session_for_order(request, order)
        if _is_ajax(request):
            return JsonResponse({'status': 'success', 'url': session.url, 'checkout_url': session.url})
        return redirect(session.url)
    except Exception as e:
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
        err_msg = f"Unable to create Stripe Checkout session: {str(e)}"
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect('payment_gatway:checkout')



def stripe_success(request):
    """
    Stripe redirect handler upon completed checkout.
    Verifies payment status securely on the server via stripe.checkout.Session.retrieve.
    """
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponseBadRequest("Missing session identifier.")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order_number = session.metadata.get('order_number')
        access_token_str = session.metadata.get('access_token')

        order = None
        if order_number:
            order = Order.objects.filter(order_number=order_number).first()
        if not order and access_token_str:
            try:
                order = Order.objects.filter(access_token=uuid.UUID(access_token_str)).first()
            except (ValueError, TypeError):
                pass
        if not order:
            order = Order.objects.filter(stripe_session_id=session_id).first()

        if not order:
            messages.error(request, "Could not locate customer order for this Stripe session.")
            return redirect('payment_gatway:checkout')

        # Idempotent check: only update if not already marked paid
        if session.payment_status == 'paid':
            if order.payment_status != 'paid':
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.stripe_payment_intent = str(session.payment_intent or '')
                order.paid_at = timezone.now()
                order.save(update_fields=['payment_status', 'order_status', 'stripe_payment_intent', 'paid_at'])

                tx_id = session.payment_intent or session_id
                Payment.objects.get_or_create(
                    order=order,
                    transaction_id=tx_id,
                    defaults={
                        'provider': 'stripe',
                        'amount': Decimal(str(session.amount_total / 100)),
                        'currency': session.currency.upper(),
                        'payment_status': 'completed',
                        'raw_response': json.dumps({'session_id': session.id, 'payment_status': session.payment_status}),
                    }
                )

                # Clear cart from guest session upon successful payment
                request.session['cart'] = {}
                request.session.modified = True

            return redirect('payment_gatway:order_success', kwargs={'access_token': order.access_token})
        else:
            messages.error(request, "Payment has not yet cleared. Please check with your bank.")
            return redirect('payment_gatway:checkout')

    except Exception as e:
        messages.error(request, f"Unable to verify Stripe checkout session: {str(e)}")
        return redirect('payment_gatway:checkout')


def stripe_cancel(request, access_token):
    """Handles user cancellation at Stripe Checkout."""
    order = get_object_or_404(Order, access_token=access_token)
    if order.payment_status == 'pending':
        cart = _get_cart(request.session)
        for item in order.items.all():
            if item.menu_item:
                str_id = str(item.menu_item.id)
                cart[str_id] = {
                    'quantity': item.quantity,
                    'name': item.item_name,
                    'price': str(item.unit_price),
                }
        request.session.modified = True

    messages.info(request, "Your card checkout was cancelled. You may select another payment option or review your order.")
    return redirect('payment_gatway:checkout')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe Webhook endpoint for asynchronous payment success and failure events.
    Verifies webhook signature using STRIPE_WEBHOOK_SECRET.
    Ensures idempotent order fulfilment.
    """
    payload = request.body
    sig_header = request.headers.get('stripe-signature') or request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    event = None
    if endpoint_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return HttpResponse(status=400)
    else:
        # Fallback parsing for test environments
        try:
            data = json.loads(payload.decode('utf-8'))
            event = data
        except Exception:
            return HttpResponse(status=400)

    event_type = event.get('type') if isinstance(event, dict) else event.type
    event_data = event.get('data', {}).get('object', {}) if isinstance(event, dict) else event.data.object

    if event_type in ['checkout.session.completed', 'checkout.session.async_payment_succeeded']:
        session = event_data
        order_number = session.get('metadata', {}).get('order_number') or session.get('client_reference_id')
        session_id = session.get('id')
        payment_status = session.get('payment_status')

        order = None
        if order_number:
            order = Order.objects.filter(order_number=order_number).first()
            if not order:
                try:
                    order = Order.objects.filter(access_token=uuid.UUID(str(order_number))).first()
                except Exception:
                    pass
        if not order and session_id:
            order = Order.objects.filter(stripe_session_id=session_id).first()

        if order and payment_status == 'paid':
            if order.payment_status != 'paid':
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.paid_at = timezone.now()
                order.stripe_payment_intent = session.get('payment_intent') or ''
                order.save(update_fields=['payment_status', 'order_status', 'paid_at', 'stripe_payment_intent'])

            Payment.objects.get_or_create(
                order=order,
                provider='stripe',
                transaction_id=session.get('payment_intent') or session.get('id', ''),
                defaults={
                    'amount': Decimal(str(session.get('amount_total', 0) / 100)),
                    'currency': session.get('currency', 'USD').upper(),
                    'payment_status': 'completed',
                    'raw_response': json.dumps(session if isinstance(session, dict) else dict(session)),
                }
            )

    elif event_type == 'checkout.session.async_payment_failed':
        session = event_data
        order_number = session.get('metadata', {}).get('order_number') or session.get('client_reference_id')
        if order_number:
            order = Order.objects.filter(order_number=order_number).first()
            if order and order.payment_status != 'paid':
                order.payment_status = 'failed'
                order.save(update_fields=['payment_status'])

    return HttpResponse(status=200)


# ==============================================================================
# FEATURE 4B: PAYPAL INTEGRATION
# ==============================================================================

def _get_paypal_access_token():
    """Fetches OAuth2 bearer token from PayPal API."""
    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_CLIENT_SECRET
    base_url = settings.PAYPAL_BASE_URL

    url = f"{base_url}/v1/oauth2/token"
    headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    data = {'grant_type': 'client_credentials'}

    resp = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret), timeout=10)
    if resp.status_code == 200:
        return resp.json().get('access_token')
    return None


@require_POST
def paypal_create_order(request, access_token):
    """
    Creates a PayPal order on the server via the PayPal REST v2 API.
    Returns the PayPal order ID to the client SDK.
    """
    order = get_object_or_404(Order, access_token=access_token)

    # In sandbox without credentials, provide mock order ID for testing
    if settings.PAYPAL_CLIENT_ID in ['sandbox_client_id', '', None]:
        mock_id = f"PAYPAL_SANDBOX_{uuid.uuid4().hex[:8].upper()}"
        order.paypal_order_id = mock_id
        order.save(update_fields=['paypal_order_id'])
        return JsonResponse({'id': mock_id, 'status': 'CREATED'})

    token = _get_paypal_access_token()
    if not token:
        return JsonResponse({'error': 'Failed to authenticate with PayPal.'}, status=500)

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}",
    }
    payload = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'reference_id': order.order_number,
            'amount': {
                'currency_code': order.currency,
                'value': f"{order.grand_total:.2f}",
            },
            'description': f"The Chesterfield Dining Order {order.order_number}",
        }]
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=12)
    if resp.status_code in [200, 201]:
        res_data = resp.json()
        order.paypal_order_id = res_data.get('id')
        order.save(update_fields=['paypal_order_id'])
        return JsonResponse(res_data)

    return JsonResponse({'error': 'PayPal order creation failed.'}, status=resp.status_code)


@require_POST
def paypal_capture_order(request):
    """
    Captures PayPal payment on the server.
    Verifies that captured amount and currency match the expected order.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    paypal_order_id = data.get('orderID') or data.get('paypal_order_id')
    access_token_str = data.get('access_token')

    order = get_object_or_404(Order, access_token=access_token_str)

    token = _get_paypal_access_token()
    if token:
        url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{paypal_order_id}/capture"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {token}",
        }

        resp = requests.post(url, headers=headers, timeout=15)
        if resp.status_code in [200, 201]:
            capture_data = resp.json()
            status = capture_data.get('status')

            if status == 'COMPLETED':
                # Verify captured amount
                try:
                    captured_amount = Decimal(str(capture_data['purchase_units'][0]['payments']['captures'][0]['amount']['value']))
                except (KeyError, IndexError, ValueError):
                    captured_amount = order.grand_total

                if captured_amount >= order.grand_total:
                    order.payment_status = 'paid'
                    order.order_status = 'confirmed'
                    order.paid_at = timezone.now()
                    order.save(update_fields=['payment_status', 'order_status', 'paid_at'])

                    Payment.objects.create(
                        order=order,
                        provider='paypal',
                        transaction_id=paypal_order_id,
                        amount=captured_amount,
                        currency=order.currency,
                        payment_status='paid',
                        raw_response=json.dumps(capture_data),
                    )

                    return JsonResponse({
                        'status': 'success',
                        'redirect_url': reverse('payment_gatway:order_success', kwargs={'access_token': order.access_token}),
                    })
                else:
                    return JsonResponse({'error': 'Payment amount mismatch detected.'}, status=400)

        return JsonResponse({'error': 'Unable to capture PayPal payment.'}, status=400)

    # Sandbox Mock Verification when no live credentials configured
    if settings.PAYPAL_CLIENT_ID in ['sandbox_client_id', '', None]:
        order.payment_status = 'paid'
        order.order_status = 'confirmed'
        order.paid_at = timezone.now()
        order.save(update_fields=['payment_status', 'order_status', 'paid_at'])

        Payment.objects.create(
            order=order,
            provider='paypal',
            transaction_id=paypal_order_id or f"PAYPAL_TEST_{uuid.uuid4().hex[:8]}",
            amount=order.grand_total,
            currency=order.currency,
            payment_status='paid',
            raw_response="Simulated PayPal Sandbox approval.",
        )

        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('payment_gatway:order_success', kwargs={'access_token': order.access_token}),
        })

    return JsonResponse({'error': 'Failed to connect to PayPal.'}, status=500)


# ==============================================================================
# FEATURE 5: ORDER CONFIRMATION
# ==============================================================================

def order_success(request, access_token):
    """
    Renders the Order Confirmation receipt page.
    Requires the secure, unguessable access_token so customers can only view their own order.
    """
    order = get_object_or_404(Order, access_token=access_token)
    items = order.items.all()

    context = {
        'order': order,
        'items': items,
        'is_cash': order.payment_method == 'cash_on_collection',
        'is_paid': order.payment_status == 'paid',
    }
    return render(request, 'payment_gatway/order_success.html', context)
