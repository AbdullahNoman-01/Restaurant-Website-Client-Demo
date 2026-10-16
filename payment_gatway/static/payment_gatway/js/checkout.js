/**
 * The Chesterfield Kitchen & Bar - Checkout Client Logic
 * Handles fulfillment toggling (Collection/Delivery), payment method switching,
 * Stripe Checkout redirect, PayPal SDK Smart Buttons, and Cash on Collection.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Utility: CSRF token
    const getCsrfToken = () => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    };

    const csrfToken = getCsrfToken();

    // DOM Elements
    const checkoutForm = document.getElementById('checkoutForm');
    const orderTypeInput = document.getElementById('orderTypeInput');
    const pillCollection = document.getElementById('pillCollection');
    const pillDelivery = document.getElementById('pillDelivery');
    const deliveryAddressGroup = document.getElementById('deliveryAddressGroup');
    const deliveryAddressInput = document.getElementById('deliveryAddress');
    const fulfillmentEstimate = document.getElementById('fulfillmentEstimate');
    const deliveryFeeEl = document.getElementById('summaryDeliveryFee');
    const grandTotalEl = document.getElementById('summaryGrandTotal');
    const subtotalEl = document.getElementById('summarySubtotal');
    const btnPlaceOrder = document.getElementById('btnPlaceOrder');
    const btnSubmitText = document.getElementById('btnSubmitText');
    const paypalContainer = document.getElementById('paypalButtonsContainer');
    const errorAlert = document.getElementById('checkoutErrorMsg');
    const paymentMethodCards = document.querySelectorAll('.payment-method-option');

    // Parse base values from DOM
    let baseSubtotal = 0;
    if (subtotalEl) {
        baseSubtotal = parseFloat(subtotalEl.textContent.replace(/[^0-9.]/g, '')) || 0;
    }

    const showError = (msg) => {
        if (errorAlert) {
            errorAlert.textContent = msg;
            errorAlert.style.display = 'block';
            errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    };

    const hideError = () => {
        if (errorAlert) {
            errorAlert.textContent = '';
            errorAlert.style.display = 'none';
        }
    };

    // 1. Fulfillment Toggle (Collection vs Delivery)
    const updateFulfillmentType = (type) => {
        hideError();
        orderTypeInput.value = type;

        if (type === 'delivery') {
            pillCollection.classList.remove('active');
            pillDelivery.classList.add('active');
            deliveryAddressGroup.style.display = 'block';
            deliveryAddressInput.setAttribute('required', 'required');
            if (fulfillmentEstimate) fulfillmentEstimate.textContent = 'Delivery estimated in 45–60 mins';

            // Calculate delivery fee
            let fee = baseSubtotal >= 50.0 ? 0.0 : 5.0;
            if (deliveryFeeEl) {
                deliveryFeeEl.innerHTML = fee === 0 ? '<span class="free-pill">FREE</span>' : `$${fee.toFixed(2)}`;
            }
            if (grandTotalEl) {
                grandTotalEl.textContent = `$${(baseSubtotal + fee).toFixed(2)}`;
            }
        } else {
            pillDelivery.classList.remove('active');
            pillCollection.classList.add('active');
            deliveryAddressGroup.style.display = 'none';
            deliveryAddressInput.removeAttribute('required');
            if (fulfillmentEstimate) fulfillmentEstimate.textContent = 'Collection ready in 25–35 mins';

            if (deliveryFeeEl) {
                deliveryFeeEl.innerHTML = '<span class="free-pill">FREE</span>';
            }
            if (grandTotalEl) {
                grandTotalEl.textContent = `$${baseSubtotal.toFixed(2)}`;
            }
        }
    };

    if (pillCollection) {
        pillCollection.addEventListener('click', () => updateFulfillmentType('collection'));
    }
    if (pillDelivery) {
        pillDelivery.addEventListener('click', () => updateFulfillmentType('delivery'));
    }

    // 2. Payment Method Switching
    const updatePaymentMethodUI = (selectedMethod) => {
        hideError();
        paymentMethodCards.forEach(card => {
            const radio = card.querySelector('input[type="radio"]');
            if (radio && radio.value === selectedMethod) {
                card.classList.add('active');
                radio.checked = true;
            } else {
                card.classList.remove('active');
            }
        });

        if (selectedMethod === 'stripe') {
            btnPlaceOrder.style.display = 'flex';
            if (paypalContainer) paypalContainer.style.display = 'none';
            btnSubmitText.textContent = 'Proceed to Stripe Checkout';
        } else if (selectedMethod === 'paypal') {
            if (window.paypal && paypalContainer) {
                btnPlaceOrder.style.display = 'none';
                paypalContainer.style.display = 'block';
                renderPayPalButtons();
            } else {
                btnPlaceOrder.style.display = 'flex';
                if (paypalContainer) paypalContainer.style.display = 'none';
                btnSubmitText.textContent = 'Continue to PayPal Checkout';
            }
        } else if (selectedMethod === 'cash_on_collection') {
            btnPlaceOrder.style.display = 'flex';
            if (paypalContainer) paypalContainer.style.display = 'none';
            btnSubmitText.textContent = 'Confirm Cash on Collection Order';
        }
    };

    paymentMethodCards.forEach(card => {
        card.addEventListener('click', () => {
            const radio = card.querySelector('input[type="radio"]');
            if (radio) {
                updatePaymentMethodUI(radio.value);
            }
        });
    });

    // 3. Form Validation Helper
    const validateFormFields = () => {
        const name = document.getElementById('custName')?.value.trim();
        const email = document.getElementById('custEmail')?.value.trim();
        const phone = document.getElementById('custPhone')?.value.trim();
        const orderType = orderTypeInput.value;
        const address = deliveryAddressInput?.value.trim();

        if (!name || !email || !phone) {
            showError('Please complete your Full Name, Email, and Telephone Number.');
            return false;
        }

        if (orderType === 'delivery' && !address) {
            showError('Please provide a complete destination delivery address.');
            return false;
        }

        return true;
    };

    // 4. Form Submission (Stripe / Cash / Fallback)
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideError();

            if (!validateFormFields()) return;

            const selectedMethod = document.querySelector('input[name="payment_method"]:checked')?.value || 'cash_on_collection';

            btnPlaceOrder.disabled = true;
            btnSubmitText.textContent = 'Securing Your Order...';

            const formData = new FormData(checkoutForm);

            try {
                const response = await fetch(checkoutForm.action, {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    },
                    body: formData
                });

                const contentType = response.headers.get('content-type') || '';
                let data = null;

                if (contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    // Check if server redirected to a success or order confirmation page
                    if (response.ok && response.redirected && response.url) {
                        window.location.href = response.url;
                        return;
                    }
                    const text = await response.text();
                    console.error('Non-JSON response from server:', text.substring(0, 300));
                    throw new Error(`Server returned unexpected format (${response.status}). Please check network or try again.`);
                }

                if (data.status === 'success') {
                    if (data.payment_method === 'cash_on_collection' && data.redirect_url) {
                        window.location.href = data.redirect_url;
                    } else if (data.payment_method === 'stripe') {
                        // Redirect directly to Stripe Hosted Checkout URL or session creation endpoint
                        const targetUrl = data.checkout_url || data.create_session_url || data.redirect_url;
                        if (targetUrl) {
                            window.location.href = targetUrl;
                        } else {
                            throw new Error('Stripe Checkout URL not returned by server.');
                        }
                    } else if (data.payment_method === 'paypal' && data.create_order_url) {
                        window.location.href = data.create_order_url;
                    } else if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                } else {
                    showError(data.message || 'An error occurred while placing your order. Please try again.');
                    btnPlaceOrder.disabled = false;
                    btnSubmitText.textContent = 'Place Order & Pay';
                }
            } catch (err) {
                console.error('Submission error:', err);
                showError(err.message || 'Network connectivity error. Please verify your connection or call the concierge.');
                btnPlaceOrder.disabled = false;
                btnSubmitText.textContent = 'Place Order & Pay';
            }
        });
    }


    // 5. PayPal SDK Smart Buttons Integration (if window.paypal is active)
    let paypalRendered = false;
    const renderPayPalButtons = () => {
        if (paypalRendered || !window.paypal || !paypalContainer) return;
        paypalRendered = true;

        window.paypal.Buttons({
            style: {
                color: 'gold',
                shape: 'rect',
                label: 'pay',
                height: 48
            },
            createOrder: async () => {
                hideError();
                if (!validateFormFields()) {
                    throw new Error('Form validation failed');
                }

                const formData = new FormData(checkoutForm);
                formData.set('payment_method', 'paypal');

                // Step 1: Place order in database to obtain access_token
                const placeRes = await fetch(checkoutForm.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    },
                    body: formData
                });

                const placeData = await placeRes.json();
                if (placeData.status !== 'success') {
                    showError(placeData.message || 'Failed to initialize order.');
                    throw new Error(placeData.message);
                }

                // Step 2: Create PayPal Order on server
                const createPaypalRes = await fetch(`/payment/paypal/create-order/${placeData.access_token}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                });

                const paypalOrderData = await createPaypalRes.json();
                if (paypalOrderData.status !== 'success') {
                    showError(paypalOrderData.message || 'Unable to establish PayPal session.');
                    throw new Error(paypalOrderData.message);
                }

                // Cache token for capture step
                window.currentOrderAccessToken = placeData.access_token;
                return paypalOrderData.paypal_order_id;
            },
            onApprove: async (data) => {
                try {
                    const captureRes = await fetch('/payment/paypal/capture-order/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            paypal_order_id: data.orderID,
                            access_token: window.currentOrderAccessToken
                        })
                    });

                    const captureData = await captureRes.json();
                    if (captureData.status === 'success' && captureData.redirect_url) {
                        window.location.href = captureData.redirect_url;
                    } else {
                        showError(captureData.message || 'PayPal payment could not be finalized.');
                    }
                } catch (err) {
                    console.error('PayPal capture error:', err);
                    showError('PayPal transaction capture failed. Please contact restaurant concierge.');
                }
            },
            onError: (err) => {
                console.error('PayPal Smart Button error:', err);
                showError('PayPal encountered an error. You may also select Credit Card or Cash on Collection.');
            }
        }).render('#paypalButtonsContainer');
    };

    // Initial payment method setup
    const initialChecked = document.querySelector('input[name="payment_method"]:checked')?.value || 'stripe';
    updatePaymentMethodUI(initialChecked);
});
