// slot603.js - JavaScript Agent for slot603 brand
(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        brand: 'slot603',
        apiKey: 'SLOT603-KEY',
        apiUrl: 'https://www.dewipemikat.com/api/report',
        localApiUrl: 'http://localhost:8000/api/report', // Fallback to local API
        expired: '2025-08-01',
        status: 'aktif',
        kategori: 'normal'
    };
    
    // Get current domain
    function getCurrentDomain() {
        return window.location.hostname;
    }
    
    // Generate report data
    function generateReportData() {
        return {
            brand: CONFIG.brand,
            domain: getCurrentDomain(),
            expired: CONFIG.expired,
            status: CONFIG.status,
            kategori: CONFIG.kategori,
            catatan: `Report from JS Agent - ${new Date().toISOString()}`,
            api_key: CONFIG.apiKey
        };
    }
    
    // Send report to API
    async function sendReport(data, apiUrl) {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'DomainMonitor-Agent/1.0'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                console.log(`[${CONFIG.brand}] Report sent successfully to ${apiUrl}`);
                return true;
            } else {
                console.warn(`[${CONFIG.brand}] Failed to send report to ${apiUrl}:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`[${CONFIG.brand}] Error sending report to ${apiUrl}:`, error);
            return false;
        }
    }
    
    // Main execution function
    async function executeAgent() {
        console.log(`[${CONFIG.brand}] Domain Monitor Agent starting...`);
        
        const reportData = generateReportData();
        console.log(`[${CONFIG.brand}] Generated report data:`, reportData);
        
        // Try external API first
        let success = await sendReport(reportData, CONFIG.apiUrl);
        
        // If external API fails, try local API
        if (!success) {
            console.log(`[${CONFIG.brand}] Trying local API as fallback...`);
            success = await sendReport(reportData, CONFIG.localApiUrl);
        }
        
        if (success) {
            console.log(`[${CONFIG.brand}] Domain monitoring report completed successfully`);
        } else {
            console.error(`[${CONFIG.brand}] Failed to send report to any API endpoint`);
        }
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeAgent);
    } else {
        executeAgent();
    }
    
    // Also send periodic reports (every 30 minutes)
    setInterval(executeAgent, 30 * 60 * 1000);
    
})();

// ============================================================================

// netpro.js - JavaScript Agent for netpro brand
(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        brand: 'netpro',
        apiKey: 'NETPRO-KEY',
        apiUrl: 'https://www.dewipemikat.com/api/report',
        localApiUrl: 'http://localhost:8000/api/report', // Fallback to local API
        expired: '2025-08-01',
        status: 'aktif',
        kategori: 'normal'
    };
    
    // Get current domain
    function getCurrentDomain() {
        return window.location.hostname;
    }
    
    // Generate report data
    function generateReportData() {
        return {
            brand: CONFIG.brand,
            domain: getCurrentDomain(),
            expired: CONFIG.expired,
            status: CONFIG.status,
            kategori: CONFIG.kategori,
            catatan: `Report from JS Agent - ${new Date().toISOString()}`,
            api_key: CONFIG.apiKey
        };
    }
    
    // Send report to API
    async function sendReport(data, apiUrl) {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'DomainMonitor-Agent/1.0'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                console.log(`[${CONFIG.brand}] Report sent successfully to ${apiUrl}`);
                return true;
            } else {
                console.warn(`[${CONFIG.brand}] Failed to send report to ${apiUrl}:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`[${CONFIG.brand}] Error sending report to ${apiUrl}:`, error);
            return false;
        }
    }
    
    // Main execution function
    async function executeAgent() {
        console.log(`[${CONFIG.brand}] Domain Monitor Agent starting...`);
        
        const reportData = generateReportData();
        console.log(`[${CONFIG.brand}] Generated report data:`, reportData);
        
        // Try external API first
        let success = await sendReport(reportData, CONFIG.apiUrl);
        
        // If external API fails, try local API
        if (!success) {
            console.log(`[${CONFIG.brand}] Trying local API as fallback...`);
            success = await sendReport(reportData, CONFIG.localApiUrl);
        }
        
        if (success) {
            console.log(`[${CONFIG.brand}] Domain monitoring report completed successfully`);
        } else {
            console.error(`[${CONFIG.brand}] Failed to send report to any API endpoint`);
        }
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeAgent);
    } else {
        executeAgent();
    }
    
    // Also send periodic reports (every 30 minutes)
    setInterval(executeAgent, 30 * 60 * 1000);
    
})();