// Main JavaScript with Reusable Functions

// Utility object for common functions
const AppUtils = {
    // Show standardized messages
    showMessage: function(message, type = 'success') {
        const alertDiv = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        $('.alert').remove();
        $('main.container').prepend(alertDiv);

        setTimeout(() => $('.alert').fadeOut('slow'), 5000);
    },

    // Format datetime consistently
    formatDateTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format currency
    formatCurrency: function(amount) {
        return '₹' + parseFloat(amount).toFixed(2);
    },

    // Get CSRF token
    getCSRFToken: function() {
        return $('[name=csrfmiddlewaretoken]').val() || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
               this.getCookie('csrftoken');
    },

    // Get cookie value
    getCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // Make API calls with standard error handling
    apiCall: function(options) {
        const defaults = {
            method: 'POST',
            contentType: 'application/json',
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    xhr.setRequestHeader("X-CSRFToken", AppUtils.getCSRFToken());
                }
            },
            success: function(response) {
                if (response.status === 'success') {
                    AppUtils.showMessage(response.message, 'success');
                } else {
                    AppUtils.showMessage(response.message || 'Operation completed', 'info');
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.message || 'An error occurred';
                AppUtils.showMessage(error, 'danger');
            }
        };

        return $.ajax($.extend(defaults, options));
    }
};

// Initialize app on document ready
$(document).ready(function() {
    // Setup tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts
    setTimeout(() => $('.alert').fadeOut('slow'), 5000);

    console.log('🍕 Food Delivery App initialized with reusable components!');
});

// Export for global use
window.AppUtils = AppUtils;
