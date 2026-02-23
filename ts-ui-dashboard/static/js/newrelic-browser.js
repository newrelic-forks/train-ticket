/**
 * New Relic Browser Agent
 * This script should be included in all HTML pages to enable browser monitoring
 */

// New Relic Browser Configuration
// The license key will be injected by the server at runtime
(function() {
    // Get configuration from server-side injected variables
    var nrConfig = window.NEW_RELIC_CONFIG || {};

    window.NREUM || (NREUM = {});
    NREUM.info = {
        "beacon": "bam.nr-data.net",
        "errorBeacon": "bam.nr-data.net",
        "licenseKey": nrConfig.browserLicenseKey || "",
        "applicationID": nrConfig.browserApplicationID || "",
        "sa": 1,
        "agent": ""
    };

    // Only initialize if we have a valid license key
    if (!NREUM.info.licenseKey) {
        console.warn('New Relic Browser monitoring disabled: No license key configured');
        return;
    }

    // Load New Relic Browser Agent
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://js-agent.newrelic.com/nr-loader-spa-1226.min.js';
    script.async = true;

    var firstScript = document.getElementsByTagName('script')[0];
    firstScript.parentNode.insertBefore(script, firstScript);

    // Custom attributes for Train Ticket application
    if (typeof newrelic !== 'undefined') {
        newrelic.setCustomAttribute('application', 'train-ticket');
        newrelic.setCustomAttribute('component', 'ui-dashboard');

        // Track page navigation
        newrelic.addPageAction('pageView', {
            page: window.location.pathname,
            referrer: document.referrer
        });
    }
})();

// Additional performance monitoring
window.addEventListener('load', function() {
    if (typeof newrelic !== 'undefined') {
        // Track page load time
        var loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        newrelic.recordMetric('Custom/PageLoad/Time', loadTime);

        // Track DOM content loaded time
        var domTime = window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart;
        newrelic.recordMetric('Custom/DOM/Time', domTime);
    }
});

// Error tracking
window.addEventListener('error', function(event) {
    if (typeof newrelic !== 'undefined') {
        newrelic.noticeError(event.error, {
            file: event.filename,
            line: event.lineno,
            column: event.colno
        });
    }
});

console.log('New Relic Browser monitoring initialized for Train Ticket UI Dashboard');