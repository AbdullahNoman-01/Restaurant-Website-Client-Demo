/**
 * ==========================================================================
 * THE CHESTERFIELD — ABOUT US JAVASCRIPT
 * Dynamic animations, counter effects, scroll observer, and timeline tracking
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    initStatsCounter();
    initScrollAnimations();
    initSmoothScroll();
    initTimelineTracker();
});

/**
 * 1. Number Counter Animation for About Stats
 */
function initStatsCounter() {
    const statsSection = document.getElementById('aboutStats');
    if (!statsSection) return;

    const statCards = statsSection.querySelectorAll('.stat-card');
    let hasAnimated = false;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasAnimated) {
                hasAnimated = true;
                statCards.forEach((card, index) => {
                    const numberEl = card.querySelector('.stat-number');
                    if (!numberEl) return;

                    const rawText = numberEl.textContent.trim();
                    // Match numeric part and symbol (e.g. 15+, 100%, 250+, 4.9★)
                    const match = rawText.match(/^([0-9.]+)(.*)$/);
                    if (!match) return;

                    const targetVal = parseFloat(match[1]);
                    const suffix = match[2] || '';
                    const isDecimal = match[1].includes('.');

                    let startVal = 0;
                    const duration = 1600 + (index * 200); // slight stagger
                    const startTime = performance.now();

                    function updateCounter(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // Ease out cubic
                        const easeProgress = 1 - Math.pow(1 - progress, 3);
                        const currentNum = startVal + (targetVal - startVal) * easeProgress;

                        if (isDecimal) {
                            numberEl.textContent = currentNum.toFixed(1) + suffix;
                        } else {
                            numberEl.textContent = Math.floor(currentNum) + suffix;
                        }

                        if (progress < 1) {
                            requestAnimationFrame(updateCounter);
                        } else {
                            numberEl.textContent = rawText;
                        }
                    }

                    requestAnimationFrame(updateCounter);
                });
            }
        });
    }, { threshold: 0.3 });

    observer.observe(statsSection);
}

/**
 * 2. Scroll Reveal Transitions
 */
function initScrollAnimations() {
    const elementsToReveal = document.querySelectorAll(
        '.story-narrative, .story-visual-column, .value-card, .team-card, .timeline-card, .about-cta-card'
    );

    if (!('IntersectionObserver' in window)) return;

    // Set initial style
    elementsToReveal.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.75s cubic-bezier(0.2, 0.8, 0.2, 1), transform 0.75s cubic-bezier(0.2, 0.8, 0.2, 1)';
    });

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    elementsToReveal.forEach(el => revealObserver.observe(el));
}

/**
 * 3. Smooth Scrolling for Internal Links
 */
function initSmoothScroll() {
    const scrollLinks = document.querySelectorAll('a[href^="#about"]');
    scrollLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * 4. Timeline Tracker Highlight
 */
function initTimelineTracker() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    if (!timelineItems.length) return;

    window.addEventListener('scroll', () => {
        const viewportCenter = window.innerHeight * 0.7;

        timelineItems.forEach(item => {
            const rect = item.getBoundingClientRect();
            const node = item.querySelector('.timeline-node');
            if (rect.top <= viewportCenter) {
                item.classList.add('timeline-active');
                if (node) {
                    node.style.borderColor = '#DFC088';
                    node.style.boxShadow = '0 0 16px rgba(197, 162, 101, 0.7)';
                }
            }
        });
    }, { passive: true });
}
