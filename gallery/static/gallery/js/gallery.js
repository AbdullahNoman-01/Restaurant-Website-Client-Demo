/**
 * THE CHESTERFIELD — VISUAL ARCHIVES & GALLERY CONTROLLER
 * Handles interactive category filtering, animated transitions,
 * museum-grade lightbox modal with keyboard navigation, and responsive touch.
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // 1. Selectors
    const filterButtons = document.querySelectorAll('.filter-pill-btn');
    const galleryCards = Array.from(document.querySelectorAll('.gallery-card'));
    const statusText = document.getElementById('galleryFilterStatus');

    // Lightbox Selectors
    const lightboxModal = document.getElementById('galleryLightboxModal');
    const lightboxBackdrop = document.getElementById('lightboxBackdrop');
    const closeBtn = document.getElementById('lightboxCloseBtn');
    const prevBtn = document.getElementById('lightboxPrevBtn');
    const nextBtn = document.getElementById('lightboxNextBtn');

    const mainImg = document.getElementById('lightboxMainImg');
    const titleEl = document.getElementById('lightboxTitle');
    const subtitleEl = document.getElementById('lightboxSubtitle');
    const descEl = document.getElementById('lightboxDesc');
    const badgeEl = document.getElementById('lightboxBadge');
    const creditEl = document.getElementById('lightboxCredit');
    const counterEl = document.getElementById('lightboxCounter');

    let currentVisibleCards = [...galleryCards];
    let currentLightboxIndex = 0;

    // 2. Filter Functionality
    if (filterButtons.length > 0) {
        filterButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                const targetFilter = this.getAttribute('data-filter');

                // Toggle active state on buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Filter cards
                currentVisibleCards = [];
                galleryCards.forEach(function (card) {
                    const cardCategory = card.getAttribute('data-category');

                    if (targetFilter === 'all' || cardCategory === targetFilter) {
                        card.style.display = '';
                        card.style.opacity = '0';
                        card.style.transform = 'scale(0.95)';
                        
                        setTimeout(function () {
                            card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
                            card.style.opacity = '1';
                            card.style.transform = 'scale(1)';
                        }, 20);

                        currentVisibleCards.push(card);
                    } else {
                        card.style.display = 'none';
                    }
                });

                // Update status indicator text
                if (statusText) {
                    const catName = button.querySelector('span:first-child') ? button.querySelector('span:first-child').textContent.trim() : '';
                    if (targetFilter === 'all') {
                        statusText.innerHTML = `Showing all <strong>${currentVisibleCards.length}</strong> photographs`;
                    } else {
                        statusText.innerHTML = `Showing <strong>${currentVisibleCards.length}</strong> photographs in <em>${catName}</em>`;
                    }
                }
            });
        });
    }

    // 3. Lightbox Population & Opening
    function openLightbox(index) {
        if (!lightboxModal || currentVisibleCards.length === 0) return;

        currentLightboxIndex = index;
        const card = currentVisibleCards[currentLightboxIndex];
        if (!card) return;

        const imgUrl = card.getAttribute('data-img') || '';
        const title = card.getAttribute('data-title') || 'The Chesterfield';
        const subtitle = card.getAttribute('data-subtitle') || '';
        const desc = card.getAttribute('data-desc') || 'A moment captured from The Chesterfield kitchen and dining hall.';
        const badge = card.getAttribute('data-badge') || 'EXCLUSIVE ARCHIVE';
        const credit = card.getAttribute('data-credit') || 'The Chesterfield Archives';

        // Animate image transition
        if (mainImg) {
            mainImg.style.opacity = '0.3';
            mainImg.src = imgUrl;
            mainImg.alt = title;
            mainImg.onload = function () {
                mainImg.style.opacity = '1';
            };
        }

        if (titleEl) titleEl.textContent = title;
        if (subtitleEl) {
            subtitleEl.textContent = subtitle;
            subtitleEl.style.display = subtitle ? 'block' : 'none';
        }
        if (descEl) descEl.textContent = desc;
        if (badgeEl) badgeEl.textContent = badge;
        if (creditEl) creditEl.textContent = credit;
        if (counterEl) counterEl.textContent = `${currentLightboxIndex + 1} / ${currentVisibleCards.length}`;

        lightboxModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        if (lightboxModal) {
            lightboxModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    function showNextImage() {
        if (currentVisibleCards.length === 0) return;
        const nextIndex = (currentLightboxIndex + 1) % currentVisibleCards.length;
        openLightbox(nextIndex);
    }

    function showPrevImage() {
        if (currentVisibleCards.length === 0) return;
        const prevIndex = (currentLightboxIndex - 1 + currentVisibleCards.length) % currentVisibleCards.length;
        openLightbox(prevIndex);
    }

    // Bind click events on gallery cards
    galleryCards.forEach(function (card) {
        card.addEventListener('click', function () {
            const visibleIndex = currentVisibleCards.indexOf(card);
            if (visibleIndex !== -1) {
                openLightbox(visibleIndex);
            }
        });
    });

    // Lightbox Controls
    if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
    if (lightboxBackdrop) lightboxBackdrop.addEventListener('click', closeLightbox);
    if (nextBtn) nextBtn.addEventListener('click', showNextImage);
    if (prevBtn) prevBtn.addEventListener('click', showPrevImage);

    // Keyboard Accessibility
    document.addEventListener('keydown', function (e) {
        if (!lightboxModal || lightboxModal.style.display === 'none') return;

        if (e.key === 'Escape') {
            closeLightbox();
        } else if (e.key === 'ArrowRight') {
            showNextImage();
        } else if (e.key === 'ArrowLeft') {
            showPrevImage();
        }
    });
});
