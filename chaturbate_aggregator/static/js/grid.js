/**
 * Grid view functionality
 * Auto-plays preview videos on hover for live rooms
 */

document.addEventListener('DOMContentLoaded', function() {
    const roomCards = document.querySelectorAll('.room-card');
    
    roomCards.forEach(card => {
        const video = card.querySelector('.room-preview-video');
        const thumbnail = card.querySelector('.room-thumbnail');
        const hlsUrl = video ? video.getAttribute('data-hls-url') : null;
        
        if (!video || !hlsUrl) return;
        
        // Initialize HLS.js for preview videos
        let hls = null;
        let isHlsInitialized = false;
        
        const initHLS = () => {
            if (isHlsInitialized) return;
            
            // Check if browser supports HLS natively
            if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = hlsUrl;
                isHlsInitialized = true;
                return;
            }
            
            // Load HLS.js if needed
            if (typeof Hls !== 'undefined') {
                if (Hls.isSupported()) {
                    hls = new Hls({
                        enableWorker: false,
                        lowLatencyMode: true
                    });
                    hls.loadSource(hlsUrl);
                    hls.attachMedia(video);
                    hls.on(Hls.Events.MANIFEST_PARSED, () => {
                        isHlsInitialized = true;
                    });
                }
            } else {
                // Load HLS.js library
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest';
                script.onload = () => {
                    if (Hls.isSupported()) {
                        hls = new Hls({
                            enableWorker: false,
                            lowLatencyMode: true
                        });
                        hls.loadSource(hlsUrl);
                        hls.attachMedia(video);
                        hls.on(Hls.Events.MANIFEST_PARSED, () => {
                            isHlsInitialized = true;
                        });
                    }
                };
                document.head.appendChild(script);
            }
        };
        
        // Play on hover
        card.addEventListener('mouseenter', () => {
            if (!isHlsInitialized) {
                initHLS();
            }
            setTimeout(() => {
                if (video.readyState >= 2) {
                    video.play().catch(err => {
                        console.log('Preview play failed:', err);
                    });
                }
            }, 300);
        });
        
        // Pause on leave
        card.addEventListener('mouseleave', () => {
            video.pause();
        });
    });
});

