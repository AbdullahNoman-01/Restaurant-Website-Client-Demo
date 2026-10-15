/**
 * ==========================================================================
 * THE CHESTERFIELD — CONTACT PAGE JAVASCRIPT
 * AJAX form submission, real-time validation, and FAQ accordion interaction
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    initContactForm();
    initFAQAccordion();
    initSmoothScroll();
});

/**
 * 1. Contact Form AJAX Submission & Validation
 */
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    const alertBox = document.getElementById('ajaxAlertBox');
    const submitBtn = document.getElementById('contactSubmitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.btn-spinner');
    const btnArrow = submitBtn.querySelector('.btn-arrow');

    const nameInput = document.getElementById('fullName');
    const emailInput = document.getElementById('emailAddress');
    const messageInput = document.getElementById('inquiryMessage');

    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const messageError = document.getElementById('messageError');

    // Email regex validation helper
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Clear error on input
    [nameInput, emailInput, messageInput].forEach(input => {
        if (!input) return;
        input.addEventListener('input', () => {
            input.classList.remove('is-invalid');
            const errEl = document.getElementById(input.id.replace('fullName', 'nameError').replace('emailAddress', 'emailError').replace('inquiryMessage', 'messageError'));
            if (errEl) {
                errEl.style.display = 'none';
                errEl.textContent = '';
            }
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        let isValid = true;

        // Reset errors
        [nameError, emailError, messageError].forEach(el => {
            if (el) { el.style.display = 'none'; el.textContent = ''; }
        });
        [nameInput, emailInput, messageInput].forEach(el => {
            if (el) el.classList.remove('is-invalid');
        });

        // Validate Full Name
        if (!nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            nameError.textContent = 'Please provide your full name.';
            nameError.style.display = 'block';
            isValid = false;
        }

        // Validate Email
        if (!emailInput.value.trim()) {
            emailInput.classList.add('is-invalid');
            emailError.textContent = 'Please provide your email address.';
            emailError.style.display = 'block';
            isValid = false;
        } else if (!isValidEmail(emailInput.value.trim())) {
            emailInput.classList.add('is-invalid');
            emailError.textContent = 'Please provide a valid email address.';
            emailError.style.display = 'block';
            isValid = false;
        }

        // Validate Message
        if (!messageInput.value.trim()) {
            messageInput.classList.add('is-invalid');
            messageError.textContent = 'Please enter your message or inquiry details.';
            messageError.style.display = 'block';
            isValid = false;
        }

        if (!isValid) return;

        // Prepare submission
        const formData = new FormData(form);
        formData.append('ajax', 'true');

        // Loading state
        submitBtn.disabled = true;
        if (btnText) btnText.textContent = 'TRANSMITTING...';
        if (btnSpinner) btnSpinner.style.display = 'inline-block';
        if (btnArrow) btnArrow.style.display = 'none';

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                // Success alert
                alertBox.className = 'ajax-alert alert alert-success';
                alertBox.innerHTML = `
                    <span class="alert-icon">✓</span>
                    <div>
                        <strong>Inquiry Transmitted Successfully</strong>
                        <p style="margin: 4px 0 0 0;">${result.message}</p>
                    </div>
                `;
                alertBox.style.display = 'flex';
                alertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

                form.reset();
            } else {
                throw new Error(result.message || 'Something went wrong while transmitting your message.');
            }
        } catch (error) {
            alertBox.className = 'ajax-alert alert alert-error';
            alertBox.innerHTML = `
                <span class="alert-icon">⚠</span>
                <div>
                    <strong>Unable to Submit</strong>
                    <p style="margin: 4px 0 0 0;">${error.message || 'Network error occurred. Please try again or telephone us directly.'}</p>
                </div>
            `;
            alertBox.style.display = 'flex';
            alertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } finally {
            // Restore button
            submitBtn.disabled = false;
            if (btnText) btnText.textContent = 'TRANSMIT INQUIRY';
            if (btnSpinner) btnSpinner.style.display = 'none';
            if (btnArrow) btnArrow.style.display = 'inline-block';
        }
    });
}

/**
 * 2. FAQ Accordion Interaction
 */
function initFAQAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    if (!faqItems.length) return;

    faqItems.forEach(item => {
        const btn = item.querySelector('.faq-question-btn');
        const panel = item.querySelector('.faq-answer-panel');

        btn.addEventListener('click', () => {
            const isOpen = item.classList.contains('faq-open');

            // Close all other panels
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('faq-open');
                    const otherBtn = otherItem.querySelector('.faq-question-btn');
                    const otherPanel = otherItem.querySelector('.faq-answer-panel');
                    if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
                    if (otherPanel) otherPanel.style.maxHeight = null;
                }
            });

            // Toggle current panel
            if (isOpen) {
                item.classList.remove('faq-open');
                btn.setAttribute('aria-expanded', 'false');
                panel.style.maxHeight = null;
            } else {
                item.classList.add('faq-open');
                btn.setAttribute('aria-expanded', 'true');
                panel.style.maxHeight = panel.scrollHeight + 30 + 'px';
            }
        });
    });
}

/**
 * 3. Smooth Scrolling for Internal Hash Anchors
 */
function initSmoothScroll() {
    const anchors = document.querySelectorAll('a[href^="#contact"]');
    anchors.forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const targetId = anchor.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}
