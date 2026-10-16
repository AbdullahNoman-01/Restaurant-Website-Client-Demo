# The Chesterfield Kitchen & Bar — Online Ordering & Payment System

A luxury modern British restaurant ordering, shopping cart, checkout, and multi-gateway payment processing system built for Django.

---

## 🍽️ Features Overview

1. **Menu & Product Details Modal:**
   - Menu cards feature **"View Details"** buttons.
   - Elegant product modal displays high-resolution culinary imagery, description, curated ingredients/features, and an interactive quantity stepper.
   - **"Add to Order"** asynchronously pushes items into the guest session cart and updates the live navbar badge.

2. **Shopping Cart (`/cart/`):**
   - Inspired by luxury dark-gold aesthetics (*Savenhoff* theme).
   - Dynamic **"When Ordering From $50 Delivery Is Free"** progress bar and tracker.
   - Itemized list with dish thumbnails, unit prices, interactive `— / +` quantity controls, line totals, and item removal (`✕`).
   - Server-side trusted pricing, live subtotal, and estimated delivery fee.

3. **Multi-Step Checkout (`/checkout/`):**
   - Progress Stepper: `Shopping Cart` → `Checkout` → `Order Confirmed`.
   - Guest details: Full name, email, phone number, and optional kitchen notes.
   - Order fulfillment toggle: **Collection (Takeaway at 56 King Street)** or **Direct Delivery** (with address validation).
   - Side summary card displaying items, subtotal, delivery fee, and grand total.

4. **Three Secure Payment Gateways:**
   - **Stripe Checkout:** Official Stripe Python SDK integration in **Test Mode**. Server-side checkout session creation, secure redirect, and signature-verified, idempotent webhook processing at `/payment/stripe/webhook/`.
   - **PayPal:** Server-side order creation and capture verification via PayPal REST v2 API (Sandbox Mode supported).
   - **Cash on Collection:** Zero-redirect order placement with `payment_method='cash_on_collection'`, `payment_status='pending'`, and instructions for counter collection.

5. **Order Confirmation & Security (`/order/<uuid:access_token>/success/`):**
   - Protected by unguessable UUID4 access tokens (prevents unauthorized access to other customers' orders).
   - Itemized summary, payment status badge, fulfillment details, and print receipt button.

6. **Django Admin Management:**
   - `Order`, `OrderItem`, and `Payment` models registered with detailed inlines, filters, and search capabilities.
   - Safe staff action: **"Mark selected Cash on Collection orders as Paid"**.
   - Strict safety rule: Admin staff cannot manually mark online Stripe/PayPal orders as 'Paid' without verified payment provider records.

---

## 🚀 Quick Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` or edit `.env`:
```env
SITE_URL=http://127.0.0.1:8000
RESTAURANT_CURRENCY=USD

# Stripe Test Mode (from https://dashboard.stripe.com/test/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal Sandbox (from https://developer.paypal.com)
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

### 3. Apply Database Migrations
```bash
python manage.py makemigrations payment_gatway
python manage.py migrate
```

### 4. Run Automated Tests
```bash
python manage.py test payment_gatway
```

### 5. Launch the Development Server
```bash
python manage.py runserver
```

---

## 💳 Payment Gateway Testing Guide

### A. Stripe Test Mode
1. Login to your Stripe Dashboard: [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys).
2. Copy your **Publishable key** (`pk_test_...`) and **Secret key** (`sk_test_...`) into `.env`.
3. To test webhooks locally using the Stripe CLI:
   ```bash
   stripe listen --forward-to localhost:8000/payment/stripe/webhook/
   ```
4. Copy the webhook signing secret output (`whsec_...`) into `STRIPE_WEBHOOK_SECRET` in `.env`.
5. Use test card numbers like `4242 4242 4242 4242` with any future expiry date and CVC `123`.

### B. PayPal Sandbox
1. Create a PayPal Sandbox App at [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/applications/sandbox).
2. Copy your **Client ID** and **Secret** into `.env`.
3. Use a PayPal Sandbox personal buyer account to test end-to-end checkout.

### C. Cash on Collection
1. Select **"Cash on Collection"** at checkout.
2. The order will immediately be confirmed without requiring any card or gateway redirect.
3. In Django Admin (`/admin/payment_gatway/order/`), staff can select the order and use the **"Mark selected Cash on Collection orders as Paid (Received at Restaurant)"** action.
