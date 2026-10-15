/**
 * THE CHESTERFIELD - Menu Interactive Logic
 * Database-backed Category filtering, smooth animations, and dynamic modal integration
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dynamic Category Tab Filtering
    const filterBtns = document.querySelectorAll('.filter-tab-btn');
    const foodCards = document.querySelectorAll('.food-card');

    if (filterBtns.length > 0 && foodCards.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active tab style
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const selectedCategory = btn.getAttribute('data-category');

                foodCards.forEach(card => {
                    const cardCategory = card.getAttribute('data-category');

                    if (selectedCategory === 'all' || cardCategory === selectedCategory) {
                        card.style.display = 'flex';
                        card.style.opacity = '0';
                        card.style.transform = 'scale(0.96)';
                        setTimeout(() => {
                            card.style.transition = 'all 0.35s ease';
                            card.style.opacity = '1';
                            card.style.transform = 'scale(1)';
                        }, 20);
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    // 2. Open Details Modal from Any Food Card
    const modalBackdrop = document.getElementById('menuDetailsBackdrop');
    const viewDetailBtns = document.querySelectorAll('.open-details-modal');

    const modalTitle = document.getElementById('modalItemTitle');
    const modalCategory = document.getElementById('modalCategory');
    const modalPrice = document.getElementById('modalPrice');
    const modalDesc = document.getElementById('modalDesc');
    const modalBadge = document.getElementById('modalBadge');
    const modalMainImg = document.getElementById('modalMainImg');
    const modalThumbsRow = document.getElementById('modalThumbsRow');
    const modalF1 = document.getElementById('modalF1');
    const modalF2 = document.getElementById('modalF2');
    const modalF3 = document.getElementById('modalF3');
    const qtyVal = document.getElementById('qtyVal');

    if (viewDetailBtns.length > 0 && modalBackdrop) {
        viewDetailBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();

                const name = btn.getAttribute('data-name');
                const categoryLabel = btn.getAttribute('data-category-label');
                const price = btn.getAttribute('data-price');
                const badge = btn.getAttribute('data-badge');
                const image = btn.getAttribute('data-image');
                const desc = btn.getAttribute('data-desc');
                const f1 = btn.getAttribute('data-f1');
                const f2 = btn.getAttribute('data-f2');
                const f3 = btn.getAttribute('data-f3');
                
                let gallery = [];
                try {
                    gallery = JSON.parse(btn.getAttribute('data-gallery') || '[]');
                } catch (err) {
                    gallery = [];
                }

                // Populate text details
                if (modalTitle) modalTitle.textContent = name || 'Gourmet Dish';
                if (modalCategory) modalCategory.textContent = categoryLabel || 'MAIN COURSE';
                if (modalPrice) modalPrice.textContent = price || '$0.00';
                if (modalDesc) modalDesc.textContent = desc || '';
                
                if (modalF1 && f1) modalF1.textContent = f1;
                if (modalF2 && f2) modalF2.textContent = f2;
                if (modalF3 && f3) modalF3.textContent = f3;

                // Badge display
                if (modalBadge) {
                    if (badge && badge.trim() !== '') {
                        modalBadge.textContent = badge;
                        modalBadge.className = `modal-popular-badge ${badge.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
                        modalBadge.style.display = 'inline-block';
                    } else {
                        modalBadge.style.display = 'none';
                    }
                }

                // Main Image
                const primaryImg = (gallery.length > 0 && gallery[0]) ? gallery[0] : image;
                if (modalMainImg && primaryImg) {
                    modalMainImg.src = primaryImg;
                }

                // Dynamic Gallery Thumbnails
                if (modalThumbsRow) {
                    modalThumbsRow.innerHTML = '';
                    const thumbsList = gallery.length > 0 ? gallery : [image];
                    
                    thumbsList.forEach((thumbSrc, idx) => {
                        const thumbBtn = document.createElement('button');
                        thumbBtn.className = `thumb-btn ${idx === 0 ? 'active' : ''}`;
                        thumbBtn.setAttribute('data-img', thumbSrc);
                        thumbBtn.innerHTML = `<img src="${thumbSrc}" alt="Thumbnail ${idx + 1}">`;

                        thumbBtn.addEventListener('click', (ev) => {
                            ev.preventDefault();
                            modalThumbsRow.querySelectorAll('.thumb-btn').forEach(t => t.classList.remove('active'));
                            thumbBtn.classList.add('active');
                            if (modalMainImg) {
                                modalMainImg.style.opacity = '0.5';
                                setTimeout(() => {
                                    modalMainImg.src = thumbSrc;
                                    modalMainImg.style.opacity = '1';
                                }, 150);
                            }
                        });

                        modalThumbsRow.appendChild(thumbBtn);
                    });
                }

                // Reset Quantity
                if (qtyVal) qtyVal.textContent = '1';

                // Open Modal
                modalBackdrop.classList.add('open');
                modalBackdrop.setAttribute('aria-hidden', 'false');
                document.body.style.overflow = 'hidden';
            });
        });
    }

    // 3. Modal Close Handlers
    const closeX = document.getElementById('detailsCloseX');
    const closeBtn = document.getElementById('modalCloseBtn');

    const closeModal = () => {
        if (modalBackdrop) {
            modalBackdrop.classList.remove('open');
            modalBackdrop.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }
    };

    if (closeX) closeX.addEventListener('click', closeModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', (e) => {
            if (e.target === modalBackdrop) {
                closeModal();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalBackdrop && modalBackdrop.classList.contains('open')) {
            closeModal();
        }
    });
});
