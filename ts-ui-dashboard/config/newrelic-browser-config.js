/**
 * New Relic Browser Configuration Generator
 * This generates the browser configuration based on environment variables
 */

// Configuration that will be injected into HTML pages
window.NEW_RELIC_CONFIG = {
    browserLicenseKey: process.env.NEW_RELIC_BROWSER_LICENSE_KEY || '',
    browserApplicationID: process.env.NEW_RELIC_BROWSER_APP_ID || '',
    enabled: (process.env.NEW_RELIC_BROWSER_ENABLED || 'true') === 'true'
};