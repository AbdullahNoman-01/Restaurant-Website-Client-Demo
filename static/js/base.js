/**
 * THE CHESTERFIELD - Modern British Kitchen & Bar
 * Base JavaScript Interactions & Behaviors
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Navigation on Scroll
    const siteHeader = document.getElementById('siteHeader');
    const handleScroll = () => {
        if (window.scrollY > 40) {
            siteHeader.classList.add('scrolled');
        } else {
            siteHeader.classList.remove('scrolled');
        }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    // 2. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mainNav = document.getElementById('mainNav');
    const navLinks = document.querySelectorAll('.nav-link');

    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', () => {
            const isOpen = mainNav.classList.toggle('open');
            mobileMenuBtn.classList.toggle('active', isOpen);
            mobileMenuBtn.setAttribute('aria-expanded', isOpen);
            document.body.style.overflow = isOpen ? 'hidden' : '';
        });

        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (mainNav.classList.contains('open')) {
                    mainNav.classList.remove('open');
                    mobileMenuBtn.classList.remove('active');
                    mobileMenuBtn.setAttribute('aria-expanded', 'false');
                    document.body.style.overflow = '';
                }
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    // 3. Reservation Modal Logic
    const bookingBackdrop = document.getElementById('bookingModalBackdrop');
    const closeBookingBtn = document.getElementById('closeBookingModal');
    const openBookingBtns = document.querySelectorAll('.open-booking-modal');
    const bookDateInput = document.getElementById('bookDate');
    const reservationForm = document.getElementById('reservationForm');
    const bookingSuccessMsg = document.getElementById('bookingSuccessMsg');

    // Set default date to tomorrow
    if (bookDateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        bookDateInput.value = tomorrow.toISOString().split('T')[0];
        bookDateInput.min = new Date().toISOString().split('T')[0];
    }

    const openBookingModal = () => {
        // If menu modal is open, close it
        closeMenuModal();
        if (bookingBackdrop) {
            bookingBackdrop.classList.add('open');
            bookingBackdrop.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
    };

    const closeBookingModal = () => {
        if (bookingBackdrop) {
            bookingBackdrop.classList.remove('open');
            bookingBackdrop.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
            // Reset form view after animation
            setTimeout(() => {
                if (reservationForm && bookingSuccessMsg) {
                    reservationForm.style.display = 'flex';
                    bookingSuccessMsg.style.display = 'none';
                    reservationForm.reset();
                }
            }, 300);
        }
    };

    openBookingBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openBookingModal();
        });
    });

    if (closeBookingBtn) {
        closeBookingBtn.addEventListener('click', closeBookingModal);
    }

    if (bookingBackdrop) {
        bookingBackdrop.addEventListener('click', (e) => {
            if (e.target === bookingBackdrop) {
                closeBookingModal();
            }
        });
    }

    // Form Submission Handling
    window.submitBooking = () => {
        if (!reservationForm.checkValidity()) {
            reservationForm.reportValidity();
            return;
        }

        const submitBtn = document.getElementById('submitBookingBtn');
        if (submitBtn) {
            submitBtn.textContent = 'CONFIRMING...';
            submitBtn.disabled = true;
        }

        setTimeout(() => {
            if (reservationForm && bookingSuccessMsg) {
                reservationForm.style.display = 'none';
                bookingSuccessMsg.style.display = 'block';
            }
            if (submitBtn) {
                submitBtn.textContent = 'CONFIRM RESERVATION';
                submitBtn.disabled = false;
            }
        }, 800);
    };

    // 4. Menu Preview Modal Logic
    const menuBackdrop = document.getElementById('menuModalBackdrop');
    const closeMenuBtn = document.getElementById('closeMenuModal');
    const openMenuBtns = document.querySelectorAll('.open-menu-modal');

    const openMenuModal = () => {
        if (menuBackdrop) {
            menuBackdrop.classList.add('open');
            menuBackdrop.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
    };

    const closeMenuModal = () => {
        if (menuBackdrop) {
            menuBackdrop.classList.remove('open');
            menuBackdrop.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }
    };

    openMenuBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openMenuModal();
        });
    });

    if (closeMenuBtn) {
        closeMenuBtn.addEventListener('click', closeMenuModal);
    }

    if (menuBackdrop) {
        menuBackdrop.addEventListener('click', (e) => {
            if (e.target === menuBackdrop) {
                closeMenuModal();
            }
        });
    }

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeBookingModal();
            closeMenuModal();
            if (mainNav && mainNav.classList.contains('open')) {
                mainNav.classList.remove('open');
                mobileMenuBtn.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });
});
