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

    // 3. Add to Order Feedback
    const initOrderBtn = (btnId) => {
        const orderBtn = document.getElementById(btnId);
        if (!orderBtn) return;

        orderBtn.addEventListener('click', () => {
            const originalHTML = orderBtn.innerHTML;
            orderBtn.disabled = true;
            orderBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>ADDED TO ORDER!</span>
            `;
            orderBtn.style.backgroundColor = '#79E298';
            orderBtn.style.color = '#0B1C10';

            setTimeout(() => {
                orderBtn.innerHTML = originalHTML;
                orderBtn.disabled = false;
                orderBtn.style.backgroundColor = '';
                orderBtn.style.color = '';
            }, 1800);
        });
    };

    initOrderBtn('modalAddOrderBtn');
    initOrderBtn('pageOrderBtn');
});
