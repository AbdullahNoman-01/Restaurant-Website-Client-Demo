/**
 * The Chesterfield Kitchen & Bar - Cart Client Logic
 * Handles interactive quantity changes, item removal, dynamic subtotal/totals,
 * free delivery progress tracker, and navbar badge synchronization.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Utility: Get Django CSRF token
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

    // Elements
    const cartWrapper = document.getElementById('cartTableWrapper');
    const emptyState = document.getElementById('cartEmptyState');
    const perkBanner = document.getElementById('deliveryPerkBanner');

    // Update Navbar cart badge if present
    const updateNavbarBadge = (count) => {
        const badge = document.getElementById('headerCartCount');
        if (badge) {
            badge.textContent = count;
            if (count > 0) {
                badge.style.display = 'inline-flex';
            } else {
                badge.style.display = 'none';
            }
        }
    };

    // Update Free Delivery Progress
    const updateDeliveryPerk = (subtotal) => {
        if (!perkBanner) return;
        const threshold = 50.0;
        const fill = perkBanner.querySelector('.perk-fill');
        const messageContainer = perkBanner.querySelector('.perk-message');

        if (subtotal >= threshold) {
            if (messageContainer) {
                messageContainer.className = 'perk-message perk-unlocked';
                messageContainer.innerHTML = `
                    <span class="perk-icon">✨</span>
                    <span class="perk-text">Congratulations! You have unlocked <strong>Free Delivery</strong> for this order.</span>
                `;
            }
            if (fill) fill.style.width = '100%';
        } else {
            const diff = (threshold - subtotal).toFixed(2);
            const percent = Math.min(Math.max((subtotal / threshold) * 100, 0), 100);
            if (messageContainer) {
                messageContainer.className = 'perk-message';
                messageContainer.innerHTML = `
                    <span class="perk-icon">🚚</span>
                    <span class="perk-text">Add <strong>$${diff}</strong> more to enjoy complimentary Free Delivery!</span>
                `;
            }
            if (fill) fill.style.width = `${percent}%`;
        }
    };

    // Update Totals UI
    const updateTotalsUI = (data) => {
        const subtotalEl = document.getElementById('cartSubtotalVal');
        const deliveryEl = document.getElementById('cartDeliveryVal');
        const grandTotalEl = document.getElementById('cartGrandTotalVal');

        if (subtotalEl) subtotalEl.textContent = `$${parseFloat(data.subtotal).toFixed(2)}`;
        if (deliveryEl) {
            if (parseFloat(data.delivery_fee) === 0) {
                deliveryEl.innerHTML = '<span class="free-text">FREE</span>';
            } else {
                deliveryEl.textContent = `$${parseFloat(data.delivery_fee).toFixed(2)}`;
            }
        }
        if (grandTotalEl) grandTotalEl.textContent = `$${parseFloat(data.grand_total).toFixed(2)}`;

        updateDeliveryPerk(parseFloat(data.subtotal));
        updateNavbarBadge(data.cart_count);

        if (data.cart_count === 0) {
            if (cartWrapper) cartWrapper.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
        }
    };

    // Quantity buttons
    document.querySelectorAll('.cart-qty-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const itemId = button.getAttribute('data-id');
            const qtyDisplay = document.getElementById(`qtyDisplay-${itemId}`);
            const lineSumDisplay = document.getElementById(`lineSum-${itemId}`);
            if (!qtyDisplay) return;

            let currentQty = parseInt(qtyDisplay.textContent, 10) || 1;
            const isPlus = button.classList.contains('btn-plus');
            let newQty = isPlus ? currentQty + 1 : currentQty - 1;

            if (newQty < 1) {
                if (confirm('Do you wish to remove this dish from your bag?')) {
                    removeItem(itemId);
                }
                return;
            }

            button.disabled = true;
            try {
                const response = await fetch('/cart/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ item_id: itemId, quantity: newQty })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    qtyDisplay.textContent = data.item_quantity;
                    if (lineSumDisplay) {
                        lineSumDisplay.textContent = `$${parseFloat(data.item_line_total).toFixed(2)}`;
                    }
                    updateTotalsUI(data);
                } else {
                    alert(data.message || 'Unable to update item quantity.');
                }
            } catch (err) {
                console.error('Error updating cart:', err);
            } finally {
                button.disabled = false;
            }
        });
    });

    // Remove Item handler
    const removeItem = async (itemId) => {
        const row = document.getElementById(`cartRow-${itemId}`);
        if (row) {
            row.style.opacity = '0.3';
            row.style.pointerEvents = 'none';
        }

        try {
            const response = await fetch('/cart/remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ item_id: itemId })
            });

            const data = await response.json();
            if (data.status === 'success') {
                if (row) {
                    row.style.transition = 'all 0.3s ease';
                    row.style.height = '0';
                    row.style.padding = '0';
                    row.style.margin = '0';
                    row.style.overflow = 'hidden';
                    setTimeout(() => row.remove(), 300);
                }
                updateTotalsUI(data);
            } else {
                if (row) {
                    row.style.opacity = '1';
                    row.style.pointerEvents = '';
                }
                alert(data.message || 'Could not remove item.');
            }
        } catch (err) {
            console.error('Error removing item:', err);
            if (row) {
                row.style.opacity = '1';
                row.style.pointerEvents = '';
            }
        }
    };

    // Remove buttons event listener
    document.querySelectorAll('.cart-remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const itemId = btn.getAttribute('data-id');
            removeItem(itemId);
        });
    });
});
