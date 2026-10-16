from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django import forms
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('item_name', 'unit_price', 'quantity', 'line_total', 'menu_item')
    readonly_fields = ('item_name', 'unit_price', 'quantity', 'line_total')
    can_delete = False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('provider', 'transaction_id', 'amount', 'currency', 'payment_status', 'created_at')
    readonly_fields = ('provider', 'transaction_id', 'amount', 'currency', 'payment_status', 'created_at')
    can_delete = False


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        payment_status = cleaned_data.get('payment_status')
        payment_method = cleaned_data.get('payment_method')

        # Safeguard: prevent staff from manually marking an online payment as paid
        # unless it is cash on collection or already verified by the payment provider
        if self.instance and self.instance.pk:
            old_order = Order.objects.get(pk=self.instance.pk)
            if old_order.payment_status != 'paid' and payment_status == 'paid':
                if payment_method in ['stripe', 'paypal']:
                    has_verified_payment = self.instance.payments.filter(
                        payment_status='paid',
                        provider=payment_method
                    ).exists()
                    if not has_verified_payment:
                        raise ValidationError(
                            f"Safety restriction: You cannot manually mark an online {payment_method.title()} order as 'Paid' "
                            f"without verified payment evidence from the payment gateway. Payment must be captured through "
                            f"the provider webhook or API capture."
                        )
        return cleaned_data


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = (
        'order_number',
        'customer_name',
        'customer_phone',
        'order_type',
        'formatted_total',
        'payment_method_badge',
        'payment_status_badge',
        'order_status',
        'created_at',
    )
    list_filter = ('order_status', 'payment_status', 'payment_method', 'order_type', 'created_at')
    search_fields = (
        'order_number',
        'customer_name',
        'customer_email',
        'customer_phone',
        'stripe_session_id',
        'paypal_order_id',
    )
    readonly_fields = (
        'order_number',
        'access_token',
        'subtotal',
        'delivery_fee',
        'grand_total',
        'currency',
        'stripe_session_id',
        'paypal_order_id',
        'created_at',
        'updated_at',
        'paid_at',
    )
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'access_token',
                'order_status',
                'order_type',
                'delivery_address',
                'special_notes',
            )
        }),
        ('Customer Details', {
            'fields': (
                'customer_name',
                'customer_email',
                'customer_phone',
            )
        }),
        ('Financial Summary', {
            'fields': (
                'currency',
                'subtotal',
                'delivery_fee',
                'grand_total',
            )
        }),
        ('Payment Gateway Details', {
            'fields': (
                'payment_method',
                'payment_status',
                'paid_at',
                'stripe_session_id',
                'paypal_order_id',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    inlines = [OrderItemInline, PaymentInline]
    actions = ['mark_cash_paid_and_confirmed']

    def formatted_total(self, obj):
        return f"${obj.grand_total:.2f} {obj.currency}"
    formatted_total.short_description = "Grand Total"

    def payment_method_badge(self, obj):
        color = "#C5A265"
        if obj.payment_method == 'stripe':
            color = "#635bff"
        elif obj.payment_method == 'paypal':
            color = "#0070ba"
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>',
            color,
            obj.get_payment_method_display()
        )
    payment_method_badge.short_description = "Method"

    def payment_status_badge(self, obj):
        colors = {
            'paid': '#28a745',
            'pending': '#ffc107',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        text_colors = {
            'pending': '#000',
        }
        bg = colors.get(obj.payment_status, '#6c757d')
        fg = text_colors.get(obj.payment_status, '#fff')
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>',
            bg,
            fg,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = "Payment Status"

    @admin.action(description="Mark selected Cash on Collection orders as Paid (Received at Restaurant)")
    def mark_cash_paid_and_confirmed(self, request, queryset):
        cash_orders = queryset.filter(payment_method='cash_on_collection')
        non_cash = queryset.exclude(payment_method='cash_on_collection')

        updated_count = 0
        for order in cash_orders:
            order.payment_status = 'paid'
            if order.order_status in ['pending', 'received']:
                order.order_status = 'confirmed'
            order.paid_at = timezone.now()
            order.save()

            # Create or update payment record
            Payment.objects.update_or_create(
                order=order,
                provider='cash',
                defaults={
                    'amount': order.grand_total,
                    'currency': order.currency,
                    'payment_status': 'paid',
                    'transaction_id': f"CASH-{order.order_number}",
                    'raw_response': {'marked_by_admin': request.user.username, 'timestamp': timezone.now().isoformat()}
                }
            )
            updated_count += 1

        if updated_count:
            self.message_user(
                request,
                f"Successfully marked {updated_count} Cash on Collection order(s) as Paid and Confirmed.",
                level=messages.SUCCESS
            )
        if non_cash.exists():
            self.message_user(
                request,
                f"Skipped {non_cash.count()} order(s) because they are online payments (Stripe/PayPal). Online payments must be verified by the gateway.",
                level=messages.WARNING
            )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order_link', 'provider', 'amount', 'currency', 'payment_status', 'created_at')
    list_filter = ('provider', 'payment_status', 'created_at')
    search_fields = ('transaction_id', 'order__order_number', 'order__customer_email', 'order__customer_name')
    readonly_fields = ('order', 'provider', 'transaction_id', 'amount', 'currency', 'payment_status', 'raw_response', 'created_at')

    def order_link(self, obj):
        return format_html('<a href="/admin/payment_gatway/order/{}/change/">{}</a>', obj.order.pk, obj.order.order_number)
    order_link.short_description = "Order"
