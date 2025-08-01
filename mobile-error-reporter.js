// Mobile Error Reporter for Production Debugging
// Add this to your frontend to capture mobile errors

class MobileErrorReporter {
    constructor(backendUrl = 'https://your-backend-url.com') {
        this.backendUrl = backendUrl;
        this.setupErrorHandling();
    }

    setupErrorHandling() {
        // Capture JavaScript errors
        window.addEventListener('error', (event) => {
            this.reportError({
                error_type: 'javascript_error',
                error_message: event.message,
                error_stack: event.error?.stack || '',
                page_url: window.location.href,
                browser_info: this.getBrowserInfo(),
                network_info: this.getNetworkInfo()
            });
        });

        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.reportError({
                error_type: 'unhandled_promise_rejection',
                error_message: event.reason?.message || String(event.reason),
                error_stack: event.reason?.stack || '',
                page_url: window.location.href,
                browser_info: this.getBrowserInfo(),
                network_info: this.getNetworkInfo()
            });
        });

        // Capture fetch errors
        this.interceptFetch();
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                // Log failed requests
                if (!response.ok) {
                    this.reportError({
                        error_type: 'fetch_error',
                        error_message: `HTTP ${response.status}: ${response.statusText}`,
                        error_stack: '',
                        page_url: window.location.href,
                        browser_info: this.getBrowserInfo(),
                        network_info: this.getNetworkInfo(),
                        request_url: args[0],
                        response_status: response.status
                    });
                }
                
                return response;
            } catch (error) {
                this.reportError({
                    error_type: 'fetch_exception',
                    error_message: error.message,
                    error_stack: error.stack || '',
                    page_url: window.location.href,
                    browser_info: this.getBrowserInfo(),
                    network_info: this.getNetworkInfo(),
                    request_url: args[0]
                });
                throw error;
            }
        };
    }

    getBrowserInfo() {
        return {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            screenWidth: screen.width,
            screenHeight: screen.height,
            windowWidth: window.innerWidth,
            windowHeight: window.innerHeight,
            devicePixelRatio: window.devicePixelRatio || 1
        };
    }

    getNetworkInfo() {
        return {
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null,
            onLine: navigator.onLine
        };
    }

    async reportError(errorData) {
        try {
            const response = await fetch(`${this.backendUrl}/api/mobile/error-report/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorData)
            });
            
            if (response.ok) {
                console.log('Error reported successfully');
            }
        } catch (error) {
            console.error('Failed to report error:', error);
        }
    }

    // Manual error reporting
    reportManualError(errorType, errorMessage, additionalData = {}) {
        this.reportError({
            error_type: errorType,
            error_message: errorMessage,
            error_stack: '',
            page_url: window.location.href,
            browser_info: this.getBrowserInfo(),
            network_info: this.getNetworkInfo(),
            ...additionalData
        });
    }
}

// Initialize the error reporter
// Replace 'https://your-backend-url.com' with your actual backend URL
const mobileErrorReporter = new MobileErrorReporter('https://your-backend-url.com');

// Export for use in other scripts
window.mobileErrorReporter = mobileErrorReporter;

// Example usage:
// mobileErrorReporter.reportManualError('login_failed', 'User could not log in on mobile device'); 