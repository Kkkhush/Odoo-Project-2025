/**
 * Optimized JavaScript for Clothing Swap Platform
 * Fast, efficient, and modern approach
 */

// Performance optimized app initialization
class ClothingSwapApp {
    constructor() {
        this.isLoaded = false;
        this.init();
    }

    init() {
        // Fast DOM ready check
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onReady());
        } else {
            this.onReady();
        }
    }

    onReady() {
        this.initializeComponents();
        this.setupEventListeners();
        this.optimizePerformance();
        this.isLoaded = true;
        console.log('🚀 App loaded in:', performance.now().toFixed(2), 'ms');
    }

    initializeComponents() {
        // Fast AOS initialization
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 300,
                easing: 'ease-out',
                once: true,
                offset: 50,
                disable: 'mobile' // Disable on mobile for better performance
            });
        }

        // Initialize search functionality
        this.setupSearch();
        
        // Initialize form validations
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Optimized scroll handler
        let scrolled = false;
        const navbar = document.querySelector('.navbar');
        
        window.addEventListener('scroll', () => {
            const shouldScroll = window.scrollY > 50;
            if (shouldScroll !== scrolled && navbar) {
                navbar.classList.toggle('scrolled', shouldScroll);
                scrolled = shouldScroll;
            }
        }, { passive: true });

        // Fast button click effects
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn')) {
                this.createRippleEffect(e);
            }
        });

        // Form submit handlers
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                this.handleFormSubmit(e);
            }
        });
    }

    createRippleEffect(e) {
        const button = e.target;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255,255,255,0.5);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.4s ease-out;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 400);
    }

    setupSearch() {
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.performSearch(e.target.value, e.target.dataset.search);
                }, 300);
            });
        });
    }

    performSearch(query, target) {
        const elements = document.querySelectorAll(`[data-searchable="${target}"]`);
        const searchTerm = query.toLowerCase();
        
        elements.forEach(element => {
            const text = element.textContent.toLowerCase();
            element.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearValidationError(input));
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid);
        
        if (!isValid) {
            this.showFieldError(field);
        }
    }

    clearValidationError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    showFieldError(field) {
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) return;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = field.validationMessage;
        field.parentNode.appendChild(errorDiv);
    }

    handleFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn && !form.checkValidity()) {
            e.preventDefault();
            this.showFormErrors(form);
            return;
        }
        
        if (submitBtn) {
            this.showLoadingState(submitBtn);
        }
    }

    showFormErrors(form) {
        const invalidFields = form.querySelectorAll(':invalid');
        invalidFields.forEach(field => this.validateField(field));
        
        if (invalidFields.length > 0) {
            invalidFields[0].focus();
        }
    }

    showLoadingState(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        button.disabled = true;
        
        // Reset after 5 seconds if form doesn't redirect
        setTimeout(() => {
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }, 5000);
    }

    optimizePerformance() {
        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }

        // Preload critical resources
        this.preloadCriticalResources();
    }

    preloadCriticalResources() {
        const criticalPaths = ['/dashboard', '/browse', '/add_item'];
        
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                criticalPaths.forEach(path => {
                    const link = document.createElement('link');
                    link.rel = 'prefetch';
                    link.href = path;
                    document.head.appendChild(link);
                });
            });
        }
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Enhanced CSS for ripple effect
const rippleCSS = `
    @keyframes ripple {
        to { transform: scale(4); opacity: 0; }
    }
    .btn { position: relative; overflow: hidden; }
    .navbar.scrolled { 
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 20px rgba(0,0,0,0.1);
    }
`;

// Inject CSS
const styleElement = document.createElement('style');
styleElement.textContent = rippleCSS;
document.head.appendChild(styleElement);

// Initialize app
const app = new ClothingSwapApp();

// Export for global access
window.ClothingSwapApp = app;
