/**
 * Live Thumbnail Auto-Refresh
 * Updates mmcdn thumbnail URLs every 0.05 seconds (1/20 second)
 * Pattern: https://thumb.live.mmcdn.com/ri/{username}.jpg?{unix_timestamp}
 */

(function() {
    'use strict';
    
    const REFRESH_INTERVAL = 50; // 0.05 seconds = 50 milliseconds
    const TIMESTAMP_INCREMENT = 0.05; // Increment timestamp by 0.05 seconds each refresh
    
    /**
     * Get current Unix timestamp with milliseconds
     */
    function getCurrentTimestamp() {
        return Date.now() / 1000; // Convert to seconds with decimals
    }
    
    /**
     * Update thumbnail src with new timestamp
     */
    function updateThumbnail(img) {
        try {
            const baseUrl = img.getAttribute('data-mmcdn-base');
            if (!baseUrl) {
                console.warn('Thumbnail missing data-mmcdn-base attribute:', img);
                return;
            }
            
            const timestamp = getCurrentTimestamp();
            // Format timestamp to 3 decimal places (milliseconds precision)
            const timestampStr = timestamp.toFixed(3);
            const newUrl = `${baseUrl}?${timestampStr}`;
            
            // Always update src to force browser to fetch new image
            // The timestamp changes every time, so URL will always be different
            // Clear any existing error state
            img.onerror = null;
            img.onload = null;
            
            // Set new src - this forces browser to fetch new image
            const oldSrc = img.src;
            img.src = newUrl;
            
            // Add error handler to catch any loading issues
            img.onerror = function() {
                console.warn('Failed to load thumbnail:', newUrl, 'Old src:', oldSrc);
            };
        } catch (error) {
            console.error('Error updating thumbnail:', error, img);
        }
    }
    
    /**
     * Initialize live thumbnail refresh for all thumbnails on page
     */
    function initLiveThumbnails() {
        // Target all mmcdn thumbnails (both live and offline)
        // Try multiple selectors to be more robust
        const liveThumbnails = document.querySelectorAll(
            '.mmcdn-thumbnail[data-mmcdn-base], ' +
            '.live-thumbnail[data-mmcdn-base], ' +
            '[data-mmcdn-base]'
        );
        
        if (liveThumbnails.length === 0) {
            console.log('No mmcdn thumbnails found to refresh. Checking page...');
            // Debug: log all images with data attributes
            const allImages = document.querySelectorAll('img[data-mmcdn-base]');
            console.log(`Found ${allImages.length} images with data-mmcdn-base attribute`);
            return; // No thumbnails to update
        }
        
        console.log(`✅ Initializing live thumbnail refresh for ${liveThumbnails.length} thumbnails`);
        console.log('Sample thumbnail:', liveThumbnails[0]);
        
        // Update all thumbnails immediately
        liveThumbnails.forEach((img, index) => {
            const baseUrl = img.getAttribute('data-mmcdn-base');
            console.log(`Updating thumbnail ${index + 1}:`, baseUrl);
            updateThumbnail(img);
            // Verify the src was updated
            setTimeout(() => {
                console.log(`  → Updated src:`, img.src.substring(0, 80) + '...');
            }, 10);
        });
        
        // Set up interval to refresh every 0.05 seconds
        // Re-query thumbnails each time to catch dynamically added ones
        const refreshInterval = setInterval(() => {
            // Re-query to get any new thumbnails that might have been added
            const currentThumbnails = document.querySelectorAll(
                '.mmcdn-thumbnail[data-mmcdn-base], ' +
                '.live-thumbnail[data-mmcdn-base], ' +
                '[data-mmcdn-base]'
            );
            currentThumbnails.forEach(updateThumbnail);
        }, REFRESH_INTERVAL);
        
        console.log(`🔄 Refresh interval started: updating every ${REFRESH_INTERVAL}ms`);
        
        // Test: log after first few updates to verify it's working
        let updateCount = 0;
        const testInterval = setInterval(() => {
            updateCount++;
            if (updateCount <= 5) {
                const firstThumb = document.querySelector('[data-mmcdn-base]');
                if (firstThumb) {
                    console.log(`Test update ${updateCount}:`, firstThumb.src.substring(0, 100));
                }
            } else {
                clearInterval(testInterval);
            }
        }, REFRESH_INTERVAL);
        
        // Clean up interval when page is hidden (save resources)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                clearInterval(refreshInterval);
            } else {
                // Restart interval when page becomes visible
                const newInterval = setInterval(() => {
                    liveThumbnails.forEach(updateThumbnail);
                }, REFRESH_INTERVAL);
                // Store interval ID for cleanup (if needed)
                window.liveThumbnailInterval = newInterval;
            }
        });
        
        // Store interval ID for potential cleanup
        window.liveThumbnailInterval = refreshInterval;
    }
    
    // Initialize when DOM is ready and images are loaded
    function startThumbnailRefresh() {
        // Wait a bit for images to render
        setTimeout(() => {
            initLiveThumbnails();
        }, 100);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startThumbnailRefresh);
    } else {
        // DOM is already ready
        startThumbnailRefresh();
    }
    
    // Also try when window loads (after all resources)
    window.addEventListener('load', () => {
        setTimeout(() => {
            initLiveThumbnails();
        }, 200);
    });
    
    // Re-initialize if new thumbnails are added dynamically
    if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver((mutations) => {
            const hasNewThumbnails = Array.from(mutations).some(mutation => {
                return Array.from(mutation.addedNodes).some(node => {
                    return node.nodeType === 1 && (
                        node.classList.contains('live-thumbnail') ||
                        node.classList.contains('mmcdn-thumbnail') ||
                        node.querySelector('.live-thumbnail') ||
                        node.querySelector('.mmcdn-thumbnail')
                    );
                });
            });
            
            if (hasNewThumbnails) {
                initLiveThumbnails();
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
})();

