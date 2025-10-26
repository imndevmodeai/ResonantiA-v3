#!/usr/bin/env python3
"""
Configuration Template for Aaron's Store Intelligence System
Copy this file to config.py and update with your actual values
"""

# Store Configuration
STORE_CONFIG = {
    "store_id": "aarons_dowagiac",
    "store_name": "Aaron's Dowagiac",
    "address": "123 Main Street, Dowagiac, MI 49047",
    "total_area_sqft": 8000,
    "zones": ["furniture", "electronics", "appliances", "accessories"],
    "operating_hours": {
        "monday": "9:00-21:00",
        "tuesday": "9:00-21:00", 
        "wednesday": "9:00-21:00",
        "thursday": "9:00-21:00",
        "friday": "9:00-21:00",
        "saturday": "9:00-21:00",
        "sunday": "10:00-18:00"
    }
}

# Data Sources Configuration
DATA_SOURCES = {
    # Aaron's Inventory System
    "inventory_api": {
        "enabled": False,  # Set to True when API is available
        "base_url": "https://your-inventory-system.com/api/v1",
        "api_key": "YOUR_API_KEY_HERE",
        "endpoints": {
            "inventory": "/inventory",
            "sales": "/sales",
            "products": "/products"
        }
    },
    
    # CSV Fallback
    "csv_source": {
        "enabled": True,
        "inventory_file": "data/inventory_export.csv",
        "sales_history_file": "data/sales_history.csv",
        "auto_refresh_minutes": 60  # Check for new files every hour
    },
    
    # Google Street View Images
    "panorama_images": {
        "directory": "data/panoramas/",
        "format": "jpg",
        "naming_convention": "pano_{id:03d}.jpg"
    }
}

# Computer Vision Settings
CV_CONFIG = {
    "confidence_threshold": 0.7,
    "clustering_epsilon": 0.3,
    "min_samples_per_cluster": 2,
    "object_detection_model": "yolo",  # Options: yolo, detectron2, custom
    "supported_object_classes": [
        "furniture", "electronics", "appliances", "decor", "accessories"
    ]
}

# Predictive Analytics Settings
ANALYTICS_CONFIG = {
    "prediction_horizon_days": 30,
    "safety_stock_days": 3,
    "supplier_lead_time_days": 7,
    "reorder_threshold_multiplier": 1.5,
    "seasonal_adjustment": True,
    "trend_analysis_window_days": 90
}

# AR/VR Interface Settings
AR_VR_CONFIG = {
    "web_interface": {
        "host": "0.0.0.0",
        "port": 5001,
        "debug": True
    },
    "ar_tracking": {
        "method": "marker",  # Options: marker, markerless, hybrid
        "marker_size": 0.1,  # meters
        "tracking_confidence_threshold": 0.8
    },
    "performance": {
        "max_concurrent_users": 50,
        "image_quality": "high",  # Options: low, medium, high
        "cache_duration_minutes": 30
    }
}

# Database Settings (Optional)
DATABASE_CONFIG = {
    "enabled": False,  # Set to True to use database storage
    "type": "sqlite",  # Options: sqlite, postgresql, mysql
    "connection": {
        "sqlite": {
            "database": "data/store_intelligence.db"
        },
        "postgresql": {
            "host": "localhost",
            "port": 5432,
            "database": "store_intelligence",
            "username": "your_username",
            "password": "your_password"
        }
    }
}

# Security Settings
SECURITY_CONFIG = {
    "manager_authentication": {
        "enabled": True,
        "username": "store_manager",
        "password": "CHANGE_THIS_PASSWORD",  # Change this!
        "session_timeout_minutes": 60
    },
    "api_rate_limiting": {
        "enabled": True,
        "requests_per_minute": 100
    },
    "cors_origins": [
        "http://localhost:3000",
        "http://localhost:5001",
        "https://your-domain.com"
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",  # Options: DEBUG, INFO, WARNING, ERROR
    "file": "logs/store_intelligence.log",
    "max_file_size_mb": 10,
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_predictive_analytics": True,
    "enable_computer_vision": True,
    "enable_ar_interface": True,
    "enable_real_time_updates": True,
    "enable_customer_analytics": False,  # Future feature
    "enable_multi_store": False  # Future feature
}

# Performance Monitoring
MONITORING_CONFIG = {
    "enabled": True,
    "metrics_collection_interval_seconds": 60,
    "alert_thresholds": {
        "response_time_ms": 2000,
        "error_rate_percent": 5.0,
        "memory_usage_percent": 80.0
    }
}

# Integration Settings
INTEGRATIONS = {
    "google_analytics": {
        "enabled": False,
        "tracking_id": "GA_TRACKING_ID"
    },
    "email_notifications": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "recipients": ["manager@aarons.com"]
    }
}

# Export configuration for easy access
__all__ = [
    'STORE_CONFIG',
    'DATA_SOURCES', 
    'CV_CONFIG',
    'ANALYTICS_CONFIG',
    'AR_VR_CONFIG',
    'DATABASE_CONFIG',
    'SECURITY_CONFIG',
    'LOGGING_CONFIG',
    'FEATURE_FLAGS',
    'MONITORING_CONFIG',
    'INTEGRATIONS'
] 