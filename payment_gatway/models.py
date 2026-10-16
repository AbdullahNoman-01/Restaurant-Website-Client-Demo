import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from menu.models import MenuItem

class Order(models.Model):
    ORDER_TYPE_CHOICES = (
        ('collection', 'Restaurant Collection (56 King Street)'),
        ('delivery', 'Direct Doorstep Delivery'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('stripe', 'Debit / Credit Card (Stripe)'),
        ('paypal', 'PayPal Online Checkout'),
        ('cash_on_collection', 'Cash on Collection (Pay at Counter)'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    )

    ORDER_STATUS_CHOICES = (
        ('received', 'Order Received'),
        ('preparing', 'In Kitchen Preparation'),
        ('ready', 'Ready for Collection / Out for Delivery'),
        ('completed', 'Completed & Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=64, unique=True, db_index=True)
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)

    # Customer Details
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50)

    # Delivery & Collection
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='collection')
    delivery_address = models.TextField(blank=True, default='')
    special_notes = models.TextField(blank=True, default='', help_text="Dietary, allergic, or kitchen instructions")

    # Financials (Calculated server-side using trusted database values)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='USD')

    # Payment & Fulfilment Status
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='cash_on_collection')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', db_index=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='received', db_index=True)

    # Gateway References
    stripe_session_id = models.CharField(max_length=255, blank=True, default='', db_index=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, default='')
    paypal_order_id = models.CharField(max_length=255, blank=True, default='', db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Order"
        verbose_name_plural = "Customer Orders"

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} (${self.grand_total})"

    @property
    def formatted_grand_total(self):
        return f"${self.grand_total:.2f}"

    @property
    def formatted_subtotal(self):
        return f"${self.subtotal:.2f}"

    @property
    def formatted_delivery_fee(self):
        if self.delivery_fee == 0:
            return "FREE"
        return f"${self.delivery_fee:.2f}"

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    
    # Snapshots (Immutable record of what was purchased at the exact price)
    item_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    item_image_url = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.item_name} (${self.line_total})"

    @property
    def formatted_unit_price(self):
        return f"${self.unit_price:.2f}"

    @property
    def formatted_line_total(self):
        return f"${self.line_total:.2f}"


class Payment(models.Model):
    PROVIDER_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash on Collection'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('completed', 'Completed & Verified'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=255, blank=True, default='', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    raw_response = models.TextField(blank=True, default='', help_text="Audit log of gateway response payload")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Record"
        verbose_name_plural = "Payment Records"

    def __str__(self):
        return f"{self.provider.upper()} - {self.transaction_id or 'Pending'} - ${self.amount} ({self.payment_status})"
