import json
import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from menu.models import Category, MenuItem
from payment_gatway.models import Order, OrderItem, Payment
from payment_gatway.admin import OrderAdminForm


class RestaurantOrderingSystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create category & menu items
        self.category = Category.objects.create(name="Main Course", slug="main-course")
        self.dish1 = MenuItem.objects.create(
            category=self.category,
            name="Roasted Venison Loin",
            price=Decimal("38.00"),
            description="Heritage beetroots, parsnip purée, blackberry port reduction.",
            is_available=True,
        )
        self.dish2 = MenuItem.objects.create(
            category=self.category,
            name="Wild Mushroom Risotto",
            price=Decimal("24.00"),
            description="Autumn chanterelles, aged Parmesan crisp, black truffle oil.",
            is_available=True,
        )

        # Staff user for admin tests
        self.staff_user = User.objects.create_superuser(
            username="admin",
            email="admin@chesterfield.test",
            password="adminpassword123"
        )

    # ==========================================================================
    # 1. Cart Tests
    # ==========================================================================
    def test_add_item_to_cart(self):
        """Test adding a menu item to the session cart."""
        url = reverse('payment_gatway:cart_add')
        response = self.client.post(
            url,
            data=json.dumps({'item_id': self.dish1.id, 'quantity': 2}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['cart_count'], 2)
        self.assertEqual(data['subtotal'], '76.00')

    def test_update_cart_quantity_and_remove(self):
        """Test updating item quantity and removing an item from the cart."""
        # Add item first
        self.client.post(
            reverse('payment_gatway:cart_add'),
            data=json.dumps({'item_id': self.dish1.id, 'quantity': 1}),
            content_type='application/json'
        )

        # Update to quantity 3
        update_url = reverse('payment_gatway:cart_update')
        response = self.client.post(
            update_url,
            data=json.dumps({'item_id': self.dish1.id, 'quantity': 3}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['cart_count'], 3)
        self.assertEqual(data['item_quantity'], 3)
        self.assertEqual(data['item_line_total'], '114.00')

        # Remove item
        remove_url = reverse('payment_gatway:cart_remove')
        rem_res = self.client.post(
            remove_url,
            data=json.dumps({'item_id': self.dish1.id}),
            content_type='application/json'
        )
        self.assertEqual(rem_res.status_code, 200)
        rem_data = rem_res.json()
        self.assertEqual(rem_data['cart_count'], 0)
        self.assertTrue(rem_data['is_empty'])

    def test_empty_cart_and_invalid_inputs(self):
        """Test cart behavior with empty cart, non-existent dish, or negative quantity."""
        # View cart when empty
        cart_url = reverse('payment_gatway:cart')
        response = self.client.get(cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Dining Bag is Empty")

        # Try adding non-existent item (should return 404)
        add_url = reverse('payment_gatway:cart_add')
        res_404 = self.client.post(
            add_url,
            data=json.dumps({'item_id': 999999, 'quantity': 1}),
            content_type='application/json'
        )
        self.assertEqual(res_404.status_code, 404)

        # Try adding with negative quantity (should default to 1)
        res_neg = self.client.post(
            add_url,
            data=json.dumps({'item_id': self.dish2.id, 'quantity': -5}),
            content_type='application/json'
        )
        self.assertEqual(res_neg.status_code, 200)
        self.assertEqual(res_neg.json()['cart_count'], 1)

    # ==========================================================================
    # 2. Server-side Price Integrity & Delivery Fee Calculation
    # ==========================================================================
    def test_server_side_price_integrity_and_free_delivery(self):
        """Ensure prices are always pulled from database and delivery fee follows rules."""
        # Add dish2 ($24.00)
        self.client.post(
            reverse('payment_gatway:cart_add'),
            data=json.dumps({'item_id': self.dish2.id, 'quantity': 1}),
            content_type='application/json'
        )

        # Test collection: delivery fee is 0 even under $50
        order_data = {
            'customer_name': 'Charles Darwin',
            'customer_email': 'charles@example.com',
            'customer_phone': '+44 7911 112233',
            'order_type': 'collection',
            'payment_method': 'cash_on_collection',
        }
        res = self.client.post(reverse('payment_gatway:place_order'), data=order_data)
        self.assertEqual(res.status_code, 302)

        order = Order.objects.latest('created_at')
        self.assertEqual(order.subtotal, Decimal('24.00'))
        self.assertEqual(order.delivery_fee, Decimal('0.00'))
        self.assertEqual(order.grand_total, Decimal('24.00'))

        # Add dish2 again for delivery (< $50: fee is $5.00)
        self.client.post(
            reverse('payment_gatway:cart_add'),
            data=json.dumps({'item_id': self.dish2.id, 'quantity': 1}),
            content_type='application/json'
        )
        order_data['order_type'] = 'delivery'
        order_data['delivery_address'] = '10 Downing Street, London'
        self.client.post(reverse('payment_gatway:place_order'), data=order_data)
        order_deliv = Order.objects.latest('created_at')
        self.assertEqual(order_deliv.subtotal, Decimal('24.00'))
        self.assertEqual(order_deliv.delivery_fee, Decimal('5.00'))
        self.assertEqual(order_deliv.grand_total, Decimal('29.00'))

        # Add 2x dish1 ($38 x 2 = $76 > $50: delivery fee is free $0.00)
        self.client.post(
            reverse('payment_gatway:cart_add'),
            data=json.dumps({'item_id': self.dish1.id, 'quantity': 2}),
            content_type='application/json'
        )
        self.client.post(reverse('payment_gatway:place_order'), data=order_data)
        order_free = Order.objects.latest('created_at')
        self.assertEqual(order_free.subtotal, Decimal('76.00'))
        self.assertEqual(order_free.delivery_fee, Decimal('0.00'))
        self.assertEqual(order_free.grand_total, Decimal('76.00'))

    # ==========================================================================
    # 3. Checkout Validation & Cash on Collection Order
    # ==========================================================================
    def test_checkout_validation_and_cash_order_creation(self):
        """Test checkout form validation and complete Cash on Collection lifecycle."""
        # Empty basket checkout attempt
        res_empty = self.client.post(
            reverse('payment_gatway:place_order'),
            data={'customer_name': 'Test'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res_empty.status_code, 400)

        # Add item
        self.client.post(
            reverse('payment_gatway:cart_add'),
            data=json.dumps({'item_id': self.dish1.id, 'quantity': 1}),
            content_type='application/json'
        )

        # Missing required customer phone
        res_missing = self.client.post(
            reverse('payment_gatway:place_order'),
            data={
                'customer_name': 'Lady Penelope',
                'customer_email': 'penelope@example.com',
                # phone is omitted
                'order_type': 'collection',
                'payment_method': 'cash_on_collection',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res_missing.status_code, 400)

        # Successful Cash on Collection order
        res_ok = self.client.post(
            reverse('payment_gatway:place_order'),
            data={
                'customer_name': 'Lady Penelope',
                'customer_email': 'penelope@example.com',
                'customer_phone': '+44 7911 556677',
                'order_type': 'collection',
                'payment_method': 'cash_on_collection',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res_ok.status_code, 200)
        data = res_ok.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['payment_method'], 'cash_on_collection')

        # Check Order & OrderItem persistence
        order = Order.objects.get(customer_email='penelope@example.com')
        self.assertEqual(order.payment_status, 'pending')
        self.assertEqual(order.order_status, 'received')
        self.assertTrue(order.order_number.startswith('TC-'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().item_name, self.dish1.name)
        self.assertEqual(order.items.first().unit_price, Decimal('38.00'))

        # Check Payment record created for cash
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.provider, 'cash')
        self.assertEqual(payment.payment_status, 'pending')

    # ==========================================================================
    # 4. Stripe Integration & Webhook Tests (Mocked)
    # ==========================================================================
    @patch('stripe.checkout.Session.create')
    def test_stripe_create_session(self, mock_stripe_create):
        """Test Stripe checkout session creation server-side."""
        mock_stripe_create.return_value = MagicMock(
            id='cs_test_mock_session_123',
            url='https://checkout.stripe.com/c/pay/cs_test_mock_session_123'
        )

        order = Order.objects.create(
            order_number='TC-20261016-STRIPE',
            customer_name='Sir Arthur',
            customer_email='arthur@example.com',
            customer_phone='+44 7123 456789',
            subtotal=Decimal('38.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('38.00'),
            payment_method='stripe',
            payment_status='pending',
            order_status='received',
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.dish1,
            item_name=self.dish1.name,
            unit_price=self.dish1.price,
            quantity=1,
            line_total=self.dish1.price
        )

        url = reverse('payment_gatway:stripe_create_session', kwargs={'access_token': order.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://checkout.stripe.com/c/pay/cs_test_mock_session_123')

        order.refresh_from_db()
        self.assertEqual(order.stripe_session_id, 'cs_test_mock_session_123')

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_and_idempotency(self, mock_webhook):
        """Test Stripe webhook signature validation, order fulfillment, and idempotency."""
        order = Order.objects.create(
            order_number='TC-20261016-WH',
            customer_name='Lord Byron',
            customer_email='byron@example.com',
            customer_phone='+44 7999 888777',
            subtotal=Decimal('38.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('38.00'),
            payment_method='stripe',
            payment_status='pending',
            order_status='received',
            stripe_session_id='cs_test_webhook_event_456'
        )

        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook_event_456',
                    'payment_status': 'paid',
                    'amount_total': 3800,
                    'currency': 'usd',
                    'client_reference_id': str(order.access_token),
                    'payment_intent': 'pi_mock_123456789',
                }
            }
        }
        mock_webhook.return_value = mock_event

        url = reverse('payment_gatway:stripe_webhook')

        # First webhook delivery
        resp1 = self.client.post(
            url,
            data=json.dumps(mock_event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='mock_signature_header'
        )
        self.assertEqual(resp1.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(order.order_status, 'confirmed')
        self.assertEqual(Payment.objects.filter(order=order, provider='stripe').count(), 1)

        # Duplicate webhook delivery (Idempotency test)
        resp2 = self.client.post(
            url,
            data=json.dumps(mock_event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='mock_signature_header'
        )
        self.assertEqual(resp2.status_code, 200)
        # Payment count must remain 1 (no duplicate record or double fulfilment)
        self.assertEqual(Payment.objects.filter(order=order, provider='stripe').count(), 1)

    # ==========================================================================
    # 5. PayPal Capture & Failure Handling (Mocked)
    # ==========================================================================
    @patch('payment_gatway.views._get_paypal_access_token')
    @patch('requests.post')
    def test_paypal_capture_and_amount_verification(self, mock_post, mock_token):
        """Test PayPal capture verification and reject mismatched amounts."""
        mock_token.return_value = 'mock_paypal_token_xyz'

        order = Order.objects.create(
            order_number='TC-20261016-PAYPAL',
            customer_name='Sir Isaac Newton',
            customer_email='newton@example.com',
            customer_phone='+44 7111 222333',
            subtotal=Decimal('24.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('24.00'),
            payment_method='paypal',
            payment_status='pending',
            order_status='received',
        )

        # Case 1: Successful capture with matching amount
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'status': 'COMPLETED',
                'purchase_units': [{
                    'payments': {
                        'captures': [{
                            'amount': {'value': '24.00', 'currency_code': 'USD'}
                        }]
                    }
                }]
            }
        )

        url = reverse('payment_gatway:paypal_capture_order')
        res = self.client.post(
            url,
            data=json.dumps({
                'paypal_order_id': 'PAYPAL_ORDER_123',
                'access_token': str(order.access_token)
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(Payment.objects.filter(order=order, provider='paypal').count(), 1)

        # Case 2: Failed capture with lower amount (attempted fraud)
        order2 = Order.objects.create(
            order_number='TC-20261016-FRAUD',
            customer_name='Shady Buyer',
            customer_email='shady@example.com',
            customer_phone='+44 7000 000000',
            subtotal=Decimal('100.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('100.00'),
            payment_method='paypal',
            payment_status='pending',
            order_status='received',
        )

        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'status': 'COMPLETED',
                'purchase_units': [{
                    'payments': {
                        'captures': [{
                            'amount': {'value': '1.00', 'currency_code': 'USD'}
                        }]
                    }
                }]
            }
        )

        res_fraud = self.client.post(
            url,
            data=json.dumps({
                'paypal_order_id': 'PAYPAL_ORDER_FAKE',
                'access_token': str(order2.access_token)
            }),
            content_type='application/json'
        )
        self.assertEqual(res_fraud.status_code, 400)
        order2.refresh_from_db()
        self.assertEqual(order2.payment_status, 'pending')

    # ==========================================================================
    # 6. Security & Order Isolation
    # ==========================================================================
    def test_order_security_and_token_isolation(self):
        """Ensure customers cannot access other customers' orders using arbitrary IDs."""
        order = Order.objects.create(
            order_number='TC-20261016-SECURE',
            customer_name='Queen Victoria',
            customer_email='victoria@example.com',
            customer_phone='+44 7999 111222',
            subtotal=Decimal('50.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('50.00'),
            payment_method='cash_on_collection',
            payment_status='pending',
        )

        # Valid unguessable token succeeds
        valid_url = reverse('payment_gatway:order_success', kwargs={'access_token': order.access_token})
        res_valid = self.client.get(valid_url)
        self.assertEqual(res_valid.status_code, 200)
        self.assertContains(res_valid, order.order_number)
        self.assertContains(res_valid, "Queen Victoria")

        # Random fake UUID returns 404
        fake_uuid = uuid.uuid4()
        fake_url = reverse('payment_gatway:order_success', kwargs={'access_token': fake_uuid})
        res_fake = self.client.get(fake_url)
        self.assertEqual(res_fake.status_code, 404)

    # ==========================================================================
    # 7. Django Admin Safeguards & Actions
    # ==========================================================================
    def test_admin_cash_action_and_online_payment_safeguard(self):
        """Test admin action for cash payments and restriction against manual online paid override."""
        self.client.login(username="admin", password="adminpassword123")

        # Cash order
        cash_order = Order.objects.create(
            order_number='TC-20261016-CASH',
            customer_name='John Watson',
            customer_email='watson@example.com',
            customer_phone='+44 7111 999888',
            subtotal=Decimal('30.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('30.00'),
            payment_method='cash_on_collection',
            payment_status='pending',
        )

        # Online order
        online_order = Order.objects.create(
            order_number='TC-20261016-ONLINE',
            customer_name='Sherlock Holmes',
            customer_email='holmes@example.com',
            customer_phone='+44 7222 333444',
            subtotal=Decimal('40.00'),
            delivery_fee=Decimal('0.00'),
            grand_total=Decimal('40.00'),
            payment_method='stripe',
            payment_status='pending',
        )

        # 1. Admin form clean validation test:
        # Trying to change online_order from pending to paid directly without gateway evidence throws ValidationError
        form = OrderAdminForm(
            instance=online_order,
            data={
                'order_number': online_order.order_number,
                'customer_name': online_order.customer_name,
                'customer_email': online_order.customer_email,
                'customer_phone': online_order.customer_phone,
                'order_type': 'collection',
                'currency': 'USD',
                'subtotal': '40.00',
                'delivery_fee': '0.00',
                'grand_total': '40.00',
                'payment_method': 'stripe',
                'payment_status': 'paid',  # Manual override without gateway payment!
                'order_status': 'received',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('Safety restriction', str(form.errors))

        # 2. Admin action test: mark cash as paid
        admin_url = reverse('admin:payment_gatway_order_changelist')
        post_data = {
            'action': 'mark_cash_paid_and_confirmed',
            '_selected_action': [cash_order.pk, online_order.pk],
        }
        res_action = self.client.post(admin_url, data=post_data, follow=True)
        self.assertEqual(res_action.status_code, 200)

        # Cash order marked as paid
        cash_order.refresh_from_db()
        self.assertEqual(cash_order.payment_status, 'paid')
        self.assertEqual(cash_order.order_status, 'confirmed')

        # Online order skipped
        online_order.refresh_from_db()
        self.assertEqual(online_order.payment_status, 'pending')
