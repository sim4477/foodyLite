// Authentication with Reusable Functions

const AuthManager = {
    currentMobile: '',
    currentRole: '',

    checkUser: function() {
        const mobileNumber = $('#mobileNumber').val().trim();

        if (!this.validateMobileNumber(mobileNumber)) {
            AppUtils.showMessage('Please enter a valid 10-digit mobile number', 'danger');
            return;
        }

        const $button = $('#loginForm button');
        $button.prop('disabled', true).text('Checking...');

        AppUtils.apiCall({
            url: '/auth/api/check-user/',
            data: JSON.stringify({
                mobile_number: mobileNumber
            }),
            success: (response) => {
                this.currentMobile = mobileNumber;
                
                if (response.data.user_exists) {
                    // User exists, OTP already sent
                    this.currentRole = response.data.user_role;
                    $('#sentToNumber').text(mobileNumber);
                    $('#loginForm').hide();
                    $('#otpForm').show();

                    if (response.data.otp) {
                        AppUtils.showMessage(`OTP sent! For demo: ${response.data.otp}`, 'info');
                        $('#otpCode').val(response.data.otp);
                    }
                } else {
                    // User doesn't exist, show role selection
                    $('#loginForm').hide();
                    $('#roleSelectionForm').show();
                    AppUtils.showMessage('New user detected. Please select your role.', 'info');
                }
            },
            complete: () => {
                $button.prop('disabled', false).text('Continue');
            }
        });
    },

    sendOTP: function() {
        const role = $('#role').val();

        if (!role) {
            AppUtils.showMessage('Please select a role', 'danger');
            return;
        }

        const $button = $('#roleSelectionForm button').first();
        $button.prop('disabled', true).text('Sending...');

        AppUtils.apiCall({
            url: '/auth/api/send-otp/',
            data: JSON.stringify({
                mobile_number: this.currentMobile,
                role: role
            }),
            success: (response) => {
                this.currentRole = role;
                $('#sentToNumber').text(this.currentMobile);
                $('#roleSelectionForm').hide();
                $('#otpForm').show();

                if (response.data && response.data.otp) {
                    AppUtils.showMessage(`OTP sent! For demo: ${response.data.otp}`, 'info');
                    $('#otpCode').val(response.data.otp);
                }
            },
            complete: () => {
                $button.prop('disabled', false).text('Send OTP');
            }
        });
    },

    verifyOTP: function() {
        const otpCode = $('#otpCode').val().trim();

        if (!this.validateOTP(otpCode)) {
            AppUtils.showMessage('Please enter the 4-digit OTP', 'danger');
            return;
        }

        const $button = $('#otpForm button').first();
        $button.prop('disabled', true).text('Verifying...');

        AppUtils.apiCall({
            url: '/auth/api/verify-otp/',
            data: JSON.stringify({
                mobile_number: this.currentMobile,
                otp_code: otpCode,
                role: this.currentRole
            }),
            success: () => {
                AppUtils.showMessage('Login successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = '/auth/dashboard/';
                }, 1500);
            },
            error: () => {
                $('#otpCode').val('').focus();
            },
            complete: () => {
                $button.prop('disabled', false).text('Verify & Login');
            }
        });
    },

    goBack: function() {
        $('#otpForm').hide();
        $('#loginForm').show();
        $('#otpCode').val('');
        this.currentMobile = '';
        this.currentRole = '';
    },

    goBackToLogin: function() {
        $('#roleSelectionForm').hide();
        $('#loginForm').show();
        this.currentMobile = '';
        this.currentRole = '';
    },

    validateMobileNumber: function(mobile) {
        return mobile && mobile.length === 10 && /^[6-9]\d{9}$/.test(mobile);
    },

    validateOTP: function(otp) {
        return otp && otp.length === 4 && /^\d{4}$/.test(otp);
    }
};

// Global functions for template usage
function checkUser() {
    AuthManager.checkUser();
}

function sendOTP() {
    AuthManager.sendOTP();
}

function verifyOTP() {
    AuthManager.verifyOTP();
}

function goBack() {
    AuthManager.goBack();
}

function goBackToLogin() {
    AuthManager.goBackToLogin();
}

// Initialize on document ready
$(document).ready(function() {
    $('#mobileNumber').focus();

    // Restrict input to numbers only
    $('#mobileNumber, #otpCode').on('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // Enter key handlers
    $('#mobileNumber').keypress(function(e) {
        if (e.which === 13) checkUser();
    });

    $('#otpCode').keypress(function(e) {
        if (e.which === 13) verifyOTP();
    });
});
