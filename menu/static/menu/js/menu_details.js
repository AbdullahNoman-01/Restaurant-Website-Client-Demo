/**
 * THE CHESTERFIELD - Menu Details Interactive Logic
 * Gallery carousel, quantity counter, and Add to Order interactions (Image 2)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Gallery Thumbnail Interaction (Works for both modal and standalone page)
    const initGallery = (thumbsContainerId, mainImgId, prevBtnId, nextBtnId) => {
        const thumbsRow = document.getElementById(thumbsContainerId);
        const mainImg = document.getElementById(mainImgId);
        const prevBtn = document.getElementById(prevBtnId);
        const nextBtn = document.getElementById(nextBtnId);

        if (!thumbsRow || !mainImg) return;

        const thumbs = thumbsRow.querySelectorAll('.thumb-btn');
        let currentIndex = 0;

        const updateMainImage = (index) => {
            if (index < 0) index = thumbs.length - 1;
            if (index >= thumbs.length) index = 0;
            currentIndex = index;

            thumbs.forEach((t, i) => t.classList.toggle('active', i === currentIndex));

            const newSrc = thumbs[currentIndex].getAttribute('data-img');
            if (newSrc) {
                mainImg.style.opacity = '0.5';
                setTimeout(() => {
                    mainImg.src = newSrc;
                    mainImg.style.opacity = '1';
                }, 150);
            }
        };

        thumbs.forEach((thumb, idx) => {
            thumb.addEventListener('click', (e) => {
                e.preventDefault();
                updateMainImage(idx);
            });
        });

        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                updateMainImage(currentIndex - 1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                updateMainImage(currentIndex + 1);
            });
        }
    };

    // Initialize for Modal Gallery
    initGallery('modalThumbsRow', 'modalMainImg', 'galleryPrevBtn', 'galleryNextBtn');

    // Initialize for Standalone Details Page Gallery
    initGallery('pageThumbsRow', 'pageMainImg', 'pageGalleryPrev', 'pageGalleryNext');

    // 2. Quantity Counter Logic
    const initQuantityCounter = (minusId, plusId, valId) => {
        const minusBtn = document.getElementById(minusId);
        const plusBtn = document.getElementById(plusId);
        const valSpan = document.getElementById(valId);

        if (!minusBtn || !plusBtn || !valSpan) return;

        let count = 1;

        minusBtn.addEventListener('click', () => {
            if (count > 1) {
                count--;
                valSpan.textContent = count;
            }
        });

        plusBtn.addEventListener('click', () => {
            if (count < 20) {
                count++;
                valSpan.textContent = count;
            }
        });
    };

    // Initialize for Modal
    initQuantityCounter('qtyMinus', 'qtyPlus', 'qtyVal');

    // Initialize for Standalone Page
    initQuantityCounter('pageQtyMinus', 'pageQtyPlus', 'pageQtyVal');

    // Utility: Get Django CSRF token
    const getCsrf = () => {
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

    const updateNavBadge = (count) => {
        const badge = document.getElementById('headerCartCount');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-flex' : 'none';
        }
    };

    // Luxury Floating Cart Toast Notification
    const showLuxuryToast = (message, cartUrl = '/cart/') => {
        let toast = document.getElementById('luxuryCartToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'luxuryCartToast';
            toast.className = 'luxury-cart-toast';
            document.body.appendChild(toast);
        }

        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">✓</div>
                <div class="toast-text">
                    <span class="toast-title">Added to Your Dining Bag</span>
                    <span class="toast-desc">${message}</span>
                </div>
                <a href="${cartUrl}" class="toast-cta-btn">VIEW BAG →</a>
                <button type="button" class="toast-close" onclick="this.closest('.luxury-cart-toast').classList.remove('show')">×</button>
            </div>
        `;

        toast.classList.add('show');
        clearTimeout(window.cartToastTimer);
        window.cartToastTimer = setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    };

    // 3. Add to Order Feedback and AJAX Call
    const initOrderBtn = (btnId, qtyValId) => {
        const orderBtn = document.getElementById(btnId);
        if (!orderBtn) return;

        orderBtn.addEventListener('click', async () => {
            const itemId = orderBtn.getAttribute('data-id');
            const qtyEl = document.getElementById(qtyValId);
            const quantity = qtyEl ? parseInt(qtyEl.textContent, 10) || 1 : 1;

            if (!itemId) {
                console.warn('No item ID found for Add to Order button.');
                return;
            }

            const originalHTML = orderBtn.innerHTML;
            orderBtn.disabled = true;
            orderBtn.innerHTML = `<span>Adding to Bag...</span>`;

            try {
                const response = await fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrf() || ''
                    },
                    body: JSON.stringify({ item_id: itemId, quantity: quantity })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    orderBtn.innerHTML = `
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        <span>ADDED! GOING TO CART...</span>
                    `;
                    orderBtn.style.backgroundColor = '#79E298';
                    orderBtn.style.color = '#0B1C10';
                    updateNavBadge(data.cart_count);
                    showLuxuryToast(`${quantity}x ${data.item_name || 'Dish'} added to your order!`, '/cart/');

                    // Redirect directly to the Cart page as requested
                    setTimeout(() => {
                        window.location.href = data.redirect_url || '/cart/';
                    }, 350);
                } else {
                    alert(data.message || 'Could not add dish to bag.');
                    orderBtn.innerHTML = originalHTML;
                    orderBtn.disabled = false;
                }
            } catch (err) {
                console.error('Error adding to order:', err);
                orderBtn.innerHTML = originalHTML;
                orderBtn.disabled = false;
            }
        });
    };

    initOrderBtn('modalAddOrderBtn', 'qtyVal');
    initOrderBtn('pageOrderBtn', 'pageQtyVal');
});
