/**
 * Auto-play preview videos on page load
 * Mimics the hover effect from cloudbate.com
 * Also handles HLS live stream playback
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize HLS.js for live stream if available
    const liveStreamPlayer = document.getElementById('live-stream-player');
    if (liveStreamPlayer && liveStreamPlayer.src) {
        // Check if browser supports HLS natively (Safari, Chrome on Android)
        if (liveStreamPlayer.canPlayType('application/vnd.apple.mpegurl')) {
            // Native HLS support - video element will handle it
            console.log('Using native HLS support');
        } else {
            // Need HLS.js library for other browsers
            // Try to load hls.js dynamically
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest';
            script.onload = function() {
                if (Hls.isSupported()) {
                    const hls = new Hls();
                    hls.loadSource(liveStreamPlayer.src);
                    hls.attachMedia(liveStreamPlayer);
                    hls.on(Hls.Events.MANIFEST_PARSED, function() {
                        liveStreamPlayer.play().catch(err => {
                            console.log('Autoplay prevented:', err);
                        });
                    });
                    console.log('HLS.js initialized for live stream');
                } else {
                    console.error('HLS.js not supported in this browser');
                }
            };
            script.onerror = function() {
                console.error('Failed to load HLS.js library');
            };
            document.head.appendChild(script);
        }
    }
    
    const performanceCards = document.querySelectorAll('.performance-card');
    
    performanceCards.forEach(card => {
        const video = card.querySelector('.preview-video');
        const thumbnail = card.querySelector('.video-thumbnail');
        const overlay = card.querySelector('.play-overlay');
        
        if (!video) return;
        
        const previewUrl = video.getAttribute('data-preview');
        if (!previewUrl) return;
        
        // Set video source
        video.src = previewUrl;
        
        // Auto-play on page load
        const playVideo = () => {
            if (video.readyState >= 2) { // HAVE_CURRENT_DATA
                video.play().catch(err => {
                    console.log('Auto-play prevented, user interaction required:', err);
                    // If autoplay fails, show thumbnail and play on click
                    if (thumbnail) {
                        thumbnail.style.display = 'block';
                    }
                    if (overlay) {
                        overlay.style.display = 'block';
                    }
                });
            } else {
                // Wait for video to load
                video.addEventListener('loadeddata', () => {
                    video.play().catch(err => {
                        console.log('Auto-play prevented:', err);
                    });
                }, { once: true });
            }
        };
        
        // Try to play immediately
        playVideo();
        
        // Also try after a short delay (for browsers that need user interaction)
        setTimeout(playVideo, 500);
        
        // Handle video events
        video.addEventListener('play', () => {
            video.classList.add('playing');
            if (thumbnail) {
                thumbnail.style.opacity = '0';
            }
            if (overlay) {
                overlay.style.opacity = '0';
            }
        });
        
        video.addEventListener('pause', () => {
            video.classList.remove('playing');
            if (thumbnail) {
                thumbnail.style.opacity = '1';
            }
            if (overlay) {
                overlay.style.opacity = '0.8';
            }
        });
        
        // Play on card hover (fallback if autoplay doesn't work)
        card.addEventListener('mouseenter', () => {
            if (!video.classList.contains('playing')) {
                video.play().catch(err => {
                    console.log('Play on hover failed:', err);
                });
            }
        });
        
        // Pause on card leave (optional - you can remove this to keep playing)
        // card.addEventListener('mouseleave', () => {
        //     video.pause();
        // });
        
        // Click to play/pause
        card.addEventListener('click', () => {
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        });
        
        // Handle video errors
        video.addEventListener('error', (e) => {
            console.error('Video error:', e);
            if (thumbnail) {
                thumbnail.style.display = 'block';
                thumbnail.style.opacity = '1';
            }
        });
    });
    
    // Intersection Observer for lazy loading/playing videos in viewport
    const observerOptions = {
        root: null,
        rootMargin: '50px',
        threshold: 0.1
    };
    
    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target.querySelector('.preview-video');
            if (!video) return;
            
            if (entry.isIntersecting) {
                // Video is in viewport, try to play
                if (video.paused) {
                    video.play().catch(err => {
                        console.log('Intersection play failed:', err);
                    });
                }
            } else {
                // Video is out of viewport, pause to save resources
                if (!video.paused) {
                    video.pause();
                }
            }
        });
    }, observerOptions);
    
    // Observe all performance cards
    performanceCards.forEach(card => {
        videoObserver.observe(card);
    });
});

