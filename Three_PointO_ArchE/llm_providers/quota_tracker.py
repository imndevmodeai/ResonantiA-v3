#!/usr/bin/env python3
"""
Quota Tracker for LLM Providers

Tracks usage, quotas, and rate limits for all LLM providers.
Supports multiple API keys per provider with individual tracking.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class QuotaInfo:
    """Information about a provider's quota and usage."""
    provider: str
    api_key_id: str  # Identifier for the API key (e.g., "groq_key_1", "groq_key_2")
    limit_type: str  # "requests_per_day", "tokens_per_day", "requests_per_minute"
    limit_value: float
    used_value: float = 0.0
    reset_time: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def is_available(self) -> bool:
        """Check if quota is available."""
        if self.reset_time and datetime.now() >= self.reset_time:
            # Reset has occurred, reset usage
            self.used_value = 0.0
            # Update reset_time to next period (for daily, next midnight)
            if self.limit_type.endswith('_per_day'):
                # Set to next midnight UTC
                self.reset_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            else:
                self.reset_time = None
            return True
        return self.used_value < self.limit_value
    
    def get_remaining(self) -> float:
        """Get remaining quota."""
        if self.reset_time and datetime.now() >= self.reset_time:
            # Reset has occurred, reset usage
            old_used = self.used_value
            self.used_value = 0.0
            # Update reset_time to next period
            if self.limit_type.endswith('_per_day'):
                # Set to next midnight UTC
                self.reset_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            else:
                self.reset_time = None
            if old_used > 0:
                logger.info(f"Quota reset: {self.provider}:{self.api_key_id} {self.limit_type} reset from {old_used:.0f} to 0")
        return max(0.0, self.limit_value - self.used_value)
    
    def get_usage_percentage(self) -> float:
        """Get usage as percentage of limit."""
        if self.limit_value == 0:
            return 0.0
        return min(100.0, (self.used_value / self.limit_value) * 100.0)


class QuotaTracker:
    """
    Tracks quotas and usage for multiple LLM providers and API keys.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize quota tracker.
        
        Args:
            storage_path: Path to JSON file for persistent storage
        """
        if storage_path is None:
            # Default to project root
            project_root = Path(__file__).parent.parent.parent
            storage_path = str(project_root / "outputs" / "llm_quota_tracker.json")
        
        self.storage_path = storage_path
        self.quotas: Dict[str, Dict[str, QuotaInfo]] = {}  # {provider: {api_key_id: QuotaInfo}}
        self._load_from_storage()
        self._initialize_default_quotas()
    
    def _load_from_storage(self):
        """Load quota data from persistent storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for provider, keys in data.items():
                        self.quotas[provider] = {}
                        for key_id, quota_data in keys.items():
                            quota_data['last_updated'] = datetime.fromisoformat(quota_data['last_updated'])
                            if quota_data.get('reset_time'):
                                quota_data['reset_time'] = datetime.fromisoformat(quota_data['reset_time'])
                            self.quotas[provider][key_id] = QuotaInfo(**quota_data)
                logger.info(f"Loaded quota data from {self.storage_path}")
        except Exception as e:
            logger.warning(f"Failed to load quota data: {e}")
            self.quotas = {}
    
    def _save_to_storage(self):
        """Save quota data to persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {}
            for provider, keys in self.quotas.items():
                data[provider] = {}
                for key_id, quota in keys.items():
                    quota_dict = asdict(quota)
                    quota_dict['last_updated'] = quota.last_updated.isoformat()
                    if quota.reset_time:
                        quota_dict['reset_time'] = quota.reset_time.isoformat()
                    data[provider][key_id] = quota_dict
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save quota data: {e}")
    
    def _initialize_default_quotas(self):
        """Initialize default quota limits for known providers."""
        defaults = {
            "groq": {
                "requests_per_day": 14400,
                "tokens_per_day": 100000,
            },
            "google": {
                "requests_per_minute": 60,  # Varies by model
                "tokens_per_minute": 16000,  # Varies by model
            },
            "mistral": {
                "requests_per_day": 10000,  # Estimated
                "tokens_per_day": 100000,  # Estimated
            },
        }
        
        # Initialize if not already present
        for provider, limits in defaults.items():
            if provider not in self.quotas:
                self.quotas[provider] = {}
    
    def register_api_key(self, provider: str, api_key_id: str, limits: Dict[str, float]):
        """
        Register a new API key with its quota limits.
        
        Args:
            provider: Provider name (e.g., "groq", "google")
            api_key_id: Unique identifier for this API key
            limits: Dictionary of limit_type -> limit_value
        """
        if provider not in self.quotas:
            self.quotas[provider] = {}
        
        # Create quota info for each limit type
        for limit_type, limit_value in limits.items():
            quota_id = f"{api_key_id}_{limit_type}"
            self.quotas[provider][quota_id] = QuotaInfo(
                provider=provider,
                api_key_id=api_key_id,
                limit_type=limit_type,
                limit_value=limit_value,
                last_updated=datetime.now()
            )
        
        self._save_to_storage()
        logger.info(f"Registered API key {api_key_id} for provider {provider}")
    
    def record_usage(self, provider: str, api_key_id: str, limit_type: str, 
                    amount: float, reset_time: Optional[datetime] = None):
        """
        Record usage for a specific provider and API key.
        Usage accumulates and persists across restarts.
        
        Args:
            provider: Provider name
            api_key_id: API key identifier
            limit_type: Type of limit (e.g., "tokens_per_day")
            amount: Amount used
            reset_time: When the quota resets (for daily limits, typically midnight UTC)
        """
        quota_id = f"{api_key_id}_{limit_type}"
        
        if provider not in self.quotas:
            self.quotas[provider] = {}
        
        if quota_id not in self.quotas[provider]:
            # Create new quota info with default limits
            self.register_api_key(provider, api_key_id, {limit_type: 1000000})  # Large default
        
        quota = self.quotas[provider][quota_id]
        
        # Check if reset has occurred before adding usage
        if quota.reset_time and datetime.now() >= quota.reset_time:
            # Reset has occurred, reset usage first
            old_used = quota.used_value
            quota.used_value = 0.0
            if old_used > 0:
                logger.info(f"Quota reset before recording: {provider}:{api_key_id} {limit_type} reset from {old_used:.0f} to 0")
        
        # Accumulate usage
        old_used = quota.used_value
        quota.used_value += amount
        quota.last_updated = datetime.now()
        
        # Set reset_time if provided, or calculate for daily limits
        if reset_time:
            quota.reset_time = reset_time
        elif limit_type.endswith('_per_day') and not quota.reset_time:
            # Set to next midnight UTC if not already set
            quota.reset_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        self._save_to_storage()
        logger.info(f"Recorded {amount:.0f} {limit_type} usage for {provider}:{api_key_id} (Total: {quota.used_value:.0f}/{quota.limit_value:.0f})")
    
    def check_availability(self, provider: str, api_key_id: str, limit_type: str, 
                         required_amount: float = 0.0) -> bool:
        """
        Check if quota is available for a request.
        
        Args:
            provider: Provider name
            api_key_id: API key identifier
            limit_type: Type of limit to check
            required_amount: Amount needed for the request
            
        Returns:
            True if quota is available, False otherwise
        """
        quota_id = f"{api_key_id}_{limit_type}"
        
        if provider not in self.quotas or quota_id not in self.quotas[provider]:
            # No quota info, assume available
            return True
        
        quota = self.quotas[provider][quota_id]
        return quota.is_available() and quota.get_remaining() >= required_amount
    
    def get_best_api_key(self, provider: str, limit_type: str, 
                        required_amount: float = 0.0) -> Optional[str]:
        """
        Get the best available API key for a provider.
        
        Args:
            provider: Provider name
            limit_type: Type of limit to check
            required_amount: Amount needed for the request
            
        Returns:
            API key ID with most remaining quota, or None if none available
        """
        if provider not in self.quotas:
            return None
        
        best_key = None
        best_remaining = -1.0
        
        # Find all keys for this provider and limit type
        for quota_id, quota in self.quotas[provider].items():
            if quota.limit_type == limit_type and quota.api_key_id:
                if quota.is_available() and quota.get_remaining() >= required_amount:
                    remaining = quota.get_remaining()
                    if remaining > best_remaining:
                        best_remaining = remaining
                        best_key = quota.api_key_id
        
        return best_key
    
    def get_usage_summary(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage summary for provider(s).
        Usage is accumulated and persisted across restarts.
        
        Args:
            provider: Provider name (None for all providers)
            
        Returns:
            Dictionary with usage summary
        """
        summary = {}
        
        providers_to_check = [provider] if provider else self.quotas.keys()
        
        for prov in providers_to_check:
            if prov not in self.quotas:
                continue
            
            summary[prov] = {}
            for quota_id, quota in self.quotas[prov].items():
                # Check and handle reset before getting summary
                if quota.reset_time and datetime.now() >= quota.reset_time:
                    # Reset has occurred, update and save
                    old_used = quota.used_value
                    quota.used_value = 0.0
                    if quota.limit_type.endswith('_per_day'):
                        quota.reset_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    else:
                        quota.reset_time = None
                    quota.last_updated = datetime.now()
                    if old_used > 0:
                        logger.info(f"Quota reset in summary: {prov}:{quota.api_key_id} {quota.limit_type} reset from {old_used:.0f} to 0")
                        self._save_to_storage()
                
                key_summary = summary[prov].setdefault(quota.api_key_id, {})
                key_summary[quota.limit_type] = {
                    "used": quota.used_value,
                    "limit": quota.limit_value,
                    "remaining": quota.get_remaining(),
                    "usage_percent": quota.get_usage_percentage(),
                    "available": quota.is_available(),
                    "reset_time": quota.reset_time.isoformat() if quota.reset_time else None,
                    "last_updated": quota.last_updated.isoformat()
                }
        
        return summary


# Global quota tracker instance
_global_quota_tracker: Optional[QuotaTracker] = None


def get_quota_tracker() -> QuotaTracker:
    """Get or create global quota tracker instance."""
    global _global_quota_tracker
    if _global_quota_tracker is None:
        _global_quota_tracker = QuotaTracker()
    return _global_quota_tracker


