
# Enhanced Mastermind Patch
# Add this to the top of mastermind/interact.py after imports

# Load enhanced configuration
try:
    with open("enhanced_mastermind_config.json", "r") as f:
        enhanced_config = json.load(f)
except FileNotFoundError:
    enhanced_config = {}

# Replace GoogleProvider initialization with rate-limited version
if enhanced_config.get("google_api", {}).get("rate_limiting", {}).get("enabled"):
    try:
        from rate_limited_llm_provider import RateLimitedGoogleProvider
        llm_provider = RateLimitedGoogleProvider(api_key=api_key)
        logger.info("✅ Rate-limited Google provider initialized")
    except ImportError:
        # Fallback to original provider
        llm_provider = GoogleProvider(api_key=api_key)
        logger.info("⚠️  Using original Google provider (rate-limited version not available)")
else:
    llm_provider = GoogleProvider(api_key=api_key)
    logger.info("✅ Standard Google provider initialized")

# Add quota monitoring
if enhanced_config.get("quota_monitoring", {}).get("enabled"):
    def log_quota_usage():
        """Log quota usage for monitoring."""
        log_file = enhanced_config["quota_monitoring"]["log_file"]
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()}: API call made\n")
    
    # Wrap the truth_seeker.seek_truth method
    original_seek_truth = truth_seeker.seek_truth
    def enhanced_seek_truth(query):
        log_quota_usage()
        return original_seek_truth(query)
    
    truth_seeker.seek_truth = enhanced_seek_truth
    logger.info("✅ Quota monitoring enabled")
