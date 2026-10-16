/**
 * ==========================================================================
 * THE CHESTERFIELD — TABLE RESERVATIONS JAVASCRIPT
 * Real-time itinerary preview, salon selection, time slots, and AJAX booking
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    initGuestSelector();
    initDatePickerSync();
    initSeatingAreaSelector();
    initTimeSlotSelector();
    initExperienceAndOccasionSync();
    initReservationFormSubmission();
    initModalControls();
    initSmoothScroll();
});

/**
 * 1. Guest Count Pills Selector
 */
function initGuestSelector() {
    const pills = document.querySelectorAll('#guestPills .guest-pill');
    const input = document.getElementById('guestsCountInput');
    const summaryVal = document.getElementById('summaryGuestsVal');
    const largePartyHint = document.getElementById('largePartyHint');

    if (!pills.length || !input) return;

    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            const count = pill.getAttribute('data-guests');
            input.value = count;

            if (summaryVal) {
                summaryVal.textContent = count === '9' ? '9+ Guests (Grand Party)' : `${count} Guests`;
            }

            if (largePartyHint) {
                largePartyHint.style.display = count === '9' ? 'block' : 'none';
            }
        });
    });
}

/**
 * 2. Date Picker Sync
 */
function initDatePickerSync() {
    const dateInput = document.getElementById('reservationDate');
    const summaryDate = document.getElementById('summaryDateVal');
    if (!dateInput || !summaryDate) return;

    function formatDisplayDate(val) {
        if (!val) return 'Select Date';
        const d = new Date(val + 'T00:00:00');
        if (isNaN(d.getTime())) return val;
        return d.toLocaleDateString('en-GB', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }

    // Set initial
    if (dateInput.value) {
        summaryDate.textContent = formatDisplayDate(dateInput.value);
    }

    dateInput.addEventListener('change', () => {
        summaryDate.textContent = formatDisplayDate(dateInput.value);
        dateInput.classList.remove('is-invalid');
        const err = document.getElementById('dateError');
        if (err) err.style.display = 'none';
    });
}

/**
 * 3. Seating Area Cards Selector
 */
function initSeatingAreaSelector() {
    const areaCards = document.querySelectorAll('.area-selection-card');
    const summaryName = document.getElementById('summaryAreaName');
    const summaryImg = document.getElementById('summaryAreaImg');

    areaCards.forEach(card => {
        card.addEventListener('click', () => {
            areaCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');

            const radio = card.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;

            const name = card.getAttribute('data-area-name');
            const img = card.getAttribute('data-area-img');

            if (summaryName && name) summaryName.textContent = name;
            if (summaryImg && img) summaryImg.src = img;
        });
    });

    // "SELECT THIS SALON" buttons from the showcase section below
    const showcaseBtns = document.querySelectorAll('.select-salon-btn');
    showcaseBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const areaId = btn.getAttribute('data-area-id');
            const targetCard = document.querySelector(`.area-selection-card[data-area-id="${areaId}"]`);
            if (targetCard) {
                targetCard.click();
                const bookingConsole = document.getElementById('bookingConsole');
                if (bookingConsole) {
                    bookingConsole.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
}

/**
 * 4. Session Tabs & Time Slot Pills
 */
function initTimeSlotSelector() {
    const sessionTabs = document.querySelectorAll('.session-tab-btn');
    const lunchSlots = document.getElementById('lunchSlots');
    const dinnerSlots = document.getElementById('dinnerSlots');
    const hiddenTime = document.getElementById('hiddenSelectedTime');
    const summaryTime = document.getElementById('summaryTimeVal');
    const allSlotPills = document.querySelectorAll('.time-slot-pill');

    // Tab toggle
    sessionTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            sessionTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const session = tab.getAttribute('data-session');
            if (session === 'lunch') {
                if (lunchSlots) lunchSlots.style.display = 'grid';
                if (dinnerSlots) dinnerSlots.style.display = 'none';
                // Activate first lunch slot if none active
                const firstLunch = lunchSlots ? lunchSlots.querySelector('.time-slot-pill') : null;
                if (firstLunch) firstLunch.click();
            } else {
                if (lunchSlots) lunchSlots.style.display = 'none';
                if (dinnerSlots) dinnerSlots.style.display = 'grid';
                // Activate 19:30 or first dinner slot
                const defDinner = dinnerSlots ? dinnerSlots.querySelector('.time-slot-pill[data-time="19:30"]') || dinnerSlots.querySelector('.time-slot-pill') : null;
                if (defDinner) defDinner.click();
            }
        });
    });

    // Time slot click
    allSlotPills.forEach(pill => {
        pill.addEventListener('click', () => {
            allSlotPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            const time = pill.getAttribute('data-time');
            if (hiddenTime) hiddenTime.value = time;
            if (summaryTime) summaryTime.textContent = time;

            const err = document.getElementById('timeError');
            if (err) err.style.display = 'none';
        });
    });
}

/**
 * 5. Experience & Occasion Sync with Summary
 */
function initExperienceAndOccasionSync() {
    const expSelect = document.getElementById('diningExperienceSelect');
    const summaryExp = document.getElementById('summaryExperienceVal');
    if (expSelect && summaryExp) {
        function updateExp() {
            const selectedText = expSelect.options[expSelect.selectedIndex].text.split('—')[0].trim();
            summaryExp.textContent = selectedText;
        }
        updateExp();
        expSelect.addEventListener('change', updateExp);
    }

    const occSelect = document.getElementById('occasionSelect');
    const summaryOcc = document.getElementById('summaryOccasionVal');
    if (occSelect && summaryOcc) {
        function updateOcc() {
            const selectedText = occSelect.options[occSelect.selectedIndex].text.split('/')[0].trim();
            summaryOcc.textContent = selectedText;
        }
        updateOcc();
        occSelect.addEventListener('change', updateOcc);
    }
}

/**
 * 6. Form Submission via AJAX & Live Confirmation Modal
 */
function initReservationFormSubmission() {
    const form = document.getElementById('mainReservationForm');
    if (!form) return;

    const alertBox = document.getElementById('bookingAjaxAlert');
    const submitBtn = document.getElementById('reservationSubmitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.btn-spinner');
    const btnArrow = submitBtn.querySelector('.btn-arrow');

    const nameInput = document.getElementById('guestName');
    const emailInput = document.getElementById('guestEmail');
    const phoneInput = document.getElementById('guestPhone');
    const dateInput = document.getElementById('reservationDate');
    const hiddenTime = document.getElementById('hiddenSelectedTime');

    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const phoneError = document.getElementById('phoneError');
    const dateError = document.getElementById('dateError');
    const timeError = document.getElementById('timeError');

    // Validation helper
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    [nameInput, emailInput, phoneInput].forEach(inp => {
        if (!inp) return;
        inp.addEventListener('input', () => {
            inp.classList.remove('is-invalid');
            const err = document.getElementById(inp.id.replace('guestName', 'nameError').replace('guestEmail', 'emailError').replace('guestPhone', 'phoneError'));
            if (err) err.style.display = 'none';
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        let isValid = true;

        // Reset errors
        [nameError, emailError, phoneError, dateError, timeError].forEach(el => {
            if (el) { el.style.display = 'none'; el.textContent = ''; }
        });
        [nameInput, emailInput, phoneInput, dateInput].forEach(el => {
            if (el) el.classList.remove('is-invalid');
        });

        // Validate Name
        if (!nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            nameError.textContent = 'Please enter the lead guest name.';
            nameError.style.display = 'block';
            isValid = false;
        }

        // Validate Email
        if (!emailInput.value.trim()) {
            emailInput.classList.add('is-invalid');
            emailError.textContent = 'Please enter an email address for your confirmation.';
            emailError.style.display = 'block';
            isValid = false;
        } else if (!isValidEmail(emailInput.value.trim())) {
            emailInput.classList.add('is-invalid');
            emailError.textContent = 'Please provide a valid email address.';
            emailError.style.display = 'block';
            isValid = false;
        }

        // Validate Phone
        if (!phoneInput.value.trim()) {
            phoneInput.classList.add('is-invalid');
            phoneError.textContent = 'Please provide a contact telephone number.';
            phoneError.style.display = 'block';
            isValid = false;
        }

        // Validate Date
        if (!dateInput.value.trim()) {
            dateInput.classList.add('is-invalid');
            dateError.textContent = 'Please select a dining date.';
            dateError.style.display = 'block';
            isValid = false;
        }

        // Validate Time
        if (!hiddenTime.value.trim()) {
            timeError.textContent = 'Please select a seating time slot.';
            timeError.style.display = 'block';
            isValid = false;
        }

        if (!isValid) return;

        // Prepare submission
        const formData = new FormData(form);

        // Loading state
        submitBtn.disabled = true;
        if (btnText) btnText.textContent = 'CONFIRMING WITH MAÎTRE D\'...';
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
                // Populate Confirmation Modal
                document.getElementById('modalRefCode').textContent = result.booking_reference;
                document.getElementById('modalGuestName').textContent = result.guest_name;
                document.getElementById('modalDate').textContent = result.date;
                document.getElementById('modalTime').textContent = result.time;
                document.getElementById('modalGuests').textContent = `${result.guests} Guests`;
                document.getElementById('modalArea').textContent = result.area;

                // Show modal
                const modal = document.getElementById('resConfirmModal');
                if (modal) modal.style.display = 'flex';

                form.reset();
            } else {
                throw new Error(result.message || 'Unable to complete reservation at this time.');
            }
        } catch (error) {
            alertBox.className = 'ajax-alert alert alert-error';
            alertBox.innerHTML = `
                <span class="alert-icon">⚠</span>
                <div>
                    <strong>Reservation Request Issue</strong>
                    <p style="margin: 4px 0 0 0;">${error.message || 'We could not complete your booking online. Please telephone 0161 839 0640 directly.'}</p>
                </div>
            `;
            alertBox.style.display = 'flex';
            alertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } finally {
            submitBtn.disabled = false;
            if (btnText) btnText.textContent = 'CONFIRM TABLE RESERVATION';
            if (btnSpinner) btnSpinner.style.display = 'none';
            if (btnArrow) btnArrow.style.display = 'inline-block';
        }
    });
}

/**
 * 7. Modal Controls
 */
function initModalControls() {
    const modal = document.getElementById('resConfirmModal');
    if (!modal) return;

    const closeBtn = document.getElementById('closeConfirmModalBtn');
    const dismissBtn = document.getElementById('modalDismissBtn');

    function closeModal() {
        modal.style.display = 'none';
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (dismissBtn) dismissBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            closeModal();
        }
    });
}

/**
 * 8. Smooth Scrolling
 */
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href === '#' || href === '#!') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}
