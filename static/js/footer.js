/**
 * THE CHESTERFIELD - Footer JavaScript Interactions
 * Newsletter subscription handler and footer behaviors
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-update Current Year
    const yearEl = document.getElementById('footerCurrentYear');
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }

    // 2. Newsletter Subscription Handling
    const newsletterForm = document.getElementById('footerNewsletterForm');
    const emailInput = document.getElementById('footerEmailInput');
    const subscribeBtn = document.getElementById('footerSubscribeBtn');
    const feedbackMsg = document.getElementById('newsletterFeedbackMsg');

    if (newsletterForm && emailInput && subscribeBtn) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const emailVal = emailInput.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailVal || !emailRegex.test(emailVal)) {
                emailInput.focus();
                emailInput.style.borderColor = '#E57373';
                setTimeout(() => {
                    emailInput.style.borderColor = '';
                }, 2000);
                return;
            }

            // Disable button & show pending state
            const originalBtnHTML = subscribeBtn.innerHTML;
            subscribeBtn.disabled = true;
            subscribeBtn.style.opacity = '0.7';
            subscribeBtn.innerHTML = '<span>SUBSCRIBING...</span>';

            setTimeout(() => {
                // Success state
                emailInput.value = '';
                subscribeBtn.style.opacity = '1';
                subscribeBtn.innerHTML = '<span>SUBSCRIBED!</span>';

                if (feedbackMsg) {
                    feedbackMsg.style.display = 'flex';
                }

                // Reset button after 3 seconds
                setTimeout(() => {
                    subscribeBtn.disabled = false;
                    subscribeBtn.innerHTML = originalBtnHTML;
                    if (feedbackMsg) {
                        feedbackMsg.style.display = 'none';
                    }
                }, 3500);
            }, 700);
        });
    }

    // 3. Smooth scrolling for internal footer links
    const footerNavLinks = document.querySelectorAll('.footer-nav-link');
    footerNavLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                const targetEl = document.querySelector(href);
                if (targetEl) {
                    e.preventDefault();
                    targetEl.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});
