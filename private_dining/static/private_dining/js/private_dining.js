/**
 * THE CHESTERFIELD — PRIVATE DINING & SALONS CONTROLLER
 * Handles salon selection pre-population, proposal inquiry AJAX submission,
 * validation feedback, and confirmation modal orchestration.
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // 1. DOM Selectors
    const inquiryForm = document.getElementById('privateInquiryForm');
    const submitBtn = document.getElementById('inquirySubmitBtn');
    const btnText = submitBtn ? submitBtn.querySelector('.btn-text') : null;
    const btnSpinner = submitBtn ? submitBtn.querySelector('.btn-spinner') : null;
    const btnArrow = submitBtn ? submitBtn.querySelector('.btn-arrow') : null;
    const ajaxAlert = document.getElementById('inquiryAjaxAlert');
    const preferredSalonSelect = document.getElementById('preferredSalon');
    const salonTriggers = document.querySelectorAll('.select-salon-trigger');

    // Modal Selectors
    const inquiryModal = document.getElementById('inquiryConfirmModal');
    const closeModalBtn = document.getElementById('closeInquiryModalBtn');
    const dismissModalBtn = document.getElementById('modalInquiryDismissBtn');
    const modalInquiryRef = document.getElementById('modalInquiryRef');
    const modalHostName = document.getElementById('modalHostName');
    const modalEventDate = document.getElementById('modalEventDate');
    const modalGuestCount = document.getElementById('modalGuestCount');
    const modalSalonName = document.getElementById('modalSalonName');

    // Form Field Selectors
    const nameInput = document.getElementById('inquiryName');
    const emailInput = document.getElementById('inquiryEmail');
    const phoneInput = document.getElementById('inquiryPhone');
    const dateInput = document.getElementById('preferredDate');

    // Error Spans
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const phoneError = document.getElementById('phoneError');
    const dateError = document.getElementById('dateError');

    // 2. Pre-select Salon Trigger Handling
    if (salonTriggers.length > 0 && preferredSalonSelect) {
        salonTriggers.forEach(function (button) {
            button.addEventListener('click', function () {
                const salonId = this.getAttribute('data-salon-id');
                const salonName = this.getAttribute('data-salon-name');

                if (salonId) {
                    preferredSalonSelect.value = salonId;
                }

                // Smooth scroll to inquiry console
                const targetConsole = document.getElementById('inquiryConsole');
                if (targetConsole) {
                    targetConsole.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }

                // Temporary highlight on the select element
                preferredSalonSelect.focus();
                preferredSalonSelect.style.borderColor = 'var(--gold-light)';
                preferredSalonSelect.style.boxShadow = '0 0 0 3px rgba(197, 162, 101, 0.4)';
                setTimeout(function () {
                    preferredSalonSelect.style.borderColor = '';
                    preferredSalonSelect.style.boxShadow = '';
                }, 2000);
            });
        });
    }

    // 3. Validation Helpers
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function clearErrors() {
        if (ajaxAlert) {
            ajaxAlert.style.display = 'none';
            ajaxAlert.textContent = '';
            ajaxAlert.className = 'ajax-alert';
        }

        const errorFields = [nameInput, emailInput, phoneInput, dateInput];
        errorFields.forEach(function (input) {
            if (input) {
                input.classList.remove('input-error');
            }
        });

        const errorSpans = [nameError, emailError, phoneError, dateError];
        errorSpans.forEach(function (span) {
            if (span) {
                span.textContent = '';
                span.classList.remove('visible');
            }
        });
    }

    function validateForm() {
        clearErrors();
        let isValid = true;

        // Name
        if (!nameInput || !nameInput.value.trim() || nameInput.value.trim().length < 2) {
            if (nameInput) nameInput.classList.add('input-error');
            if (nameError) {
                nameError.textContent = 'Please specify your full name or title.';
                nameError.classList.add('visible');
            }
            isValid = false;
        }

        // Email
        if (!emailInput || !emailInput.value.trim() || !isValidEmail(emailInput.value.trim())) {
            if (emailInput) emailInput.classList.add('input-error');
            if (emailError) {
                emailError.textContent = 'Please provide a valid electronic mail address.';
                emailError.classList.add('visible');
            }
            isValid = false;
        }

        // Phone
        if (!phoneInput || !phoneInput.value.trim() || phoneInput.value.trim().length < 7) {
            if (phoneInput) phoneInput.classList.add('input-error');
            if (phoneError) {
                phoneError.textContent = 'Please provide a direct telephone number for our event director.';
                phoneError.classList.add('visible');
            }
            isValid = false;
        }

        // Date
        if (!dateInput || !dateInput.value) {
            if (dateInput) dateInput.classList.add('input-error');
            if (dateError) {
                dateError.textContent = 'Please indicate your requested event date.';
                dateError.classList.add('visible');
            }
            isValid = false;
        }

        return isValid;
    }

    // 4. AJAX Submission
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', function (event) {
            event.preventDefault();

            if (!validateForm()) {
                return;
            }

            // Button loading state
            if (submitBtn) {
                submitBtn.disabled = true;
                if (btnText) btnText.textContent = 'TRANSMITTING PROPOSAL DOSSIER...';
                if (btnSpinner) btnSpinner.style.display = 'inline-block';
                if (btnArrow) btnArrow.style.display = 'none';
            }

            const formData = new FormData(inquiryForm);
            formData.set('ajax', 'true');

            fetch(inquiryForm.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            })
            .then(function (result) {
                if (result.ok && result.data.status === 'success') {
                    // Populate modal
                    if (modalInquiryRef) modalInquiryRef.textContent = result.data.reference_id || 'PD-CONFIRMED';
                    if (modalHostName) modalHostName.textContent = result.data.full_name || 'Honoured Guest';
                    if (modalEventDate) modalEventDate.textContent = result.data.date || 'Arrangement Confirmed';
                    if (modalGuestCount) modalGuestCount.textContent = (result.data.guests || '12') + ' Guests';
                    if (modalSalonName) modalSalonName.textContent = result.data.salon || 'Executive Private Salon';

                    // Show Confirmation Modal
                    if (inquiryModal) {
                        inquiryModal.style.display = 'flex';
                        document.body.style.overflow = 'hidden';
                    }

                    // Reset form
                    inquiryForm.reset();
                    clearErrors();
                } else {
                    const errorMsg = (result.data && result.data.message) ? result.data.message : 'An error occurred while transmitting your proposal request. Please call our director directly.';
                    showAjaxAlert(errorMsg, 'error');
                }
            })
            .catch(function (error) {
                console.error('Inquiry Submission Error:', error);
                showAjaxAlert('Unable to reach the server. Please check your network connection or phone our director at 0161 839 0642.', 'error');
            })
            .finally(function () {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    if (btnText) btnText.textContent = 'TRANSMIT PROPOSAL REQUEST';
                    if (btnSpinner) btnSpinner.style.display = 'none';
                    if (btnArrow) btnArrow.style.display = 'inline-block';
                }
            });
        });
    }

    function showAjaxAlert(message, type) {
        if (!ajaxAlert) return;
        ajaxAlert.textContent = message;
        ajaxAlert.className = 'ajax-alert alert-' + type;
        ajaxAlert.style.display = 'block';
        ajaxAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // 5. Modal Close Controls
    function closeModal() {
        if (inquiryModal) {
            inquiryModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    if (dismissModalBtn) {
        dismissModalBtn.addEventListener('click', closeModal);
    }

    window.addEventListener('click', function (e) {
        if (e.target === inquiryModal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && inquiryModal && inquiryModal.style.display === 'flex') {
            closeModal();
        }
    });
});
