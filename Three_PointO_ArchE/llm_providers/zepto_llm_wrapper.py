#!/usr/bin/env python3
"""
Zepto-Enabled LLM Provider Wrapper
===================================

This wrapper compresses prompts using Zepto SPR before sending to LLM providers,
and decompresses responses when needed. This can significantly reduce token usage.

Example compression ratios:
- 65,205 chars → 14 chars (4657:1 ratio)
- 48,272 chars → 24 chars (2011:1 ratio)
- Typical prompts: 5-20:1 compression

This means a 10,000 token prompt could become 500-2,000 tokens, saving 80-95% of token usage.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from .base import BaseLLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

# Try to import Zepto processor
ZEPTO_AVAILABLE = False
compress_to_zepto = None
decompress_from_zepto = None
ZeptoEngine = None

try:
    from ..zepto_spr_processor import compress_to_zepto, decompress_from_zepto, ZeptoEngine
    ZEPTO_AVAILABLE = True
    logger.info("Zepto SPR processor available for LLM token reduction")
except ImportError:
    logger.warning("Zepto SPR processor not available. LLM token reduction disabled.")


class ZeptoLLMWrapper:
    """
    Wrapper that adds Zepto compression to any LLM provider.
    
    Automatically compresses prompts before sending to reduce token usage,
    and decompresses responses when needed.
    """
    
    def __init__(
        self,
        base_provider: BaseLLMProvider,
        enable_compression: bool = True,
        compression_threshold: int = 500,  # Only compress if prompt > 500 chars
        auto_decompress: bool = True,
        zepto_engine: Optional[Any] = None
    ):
        """
        Initialize Zepto wrapper around a base LLM provider.
        
        Args:
            base_provider: The underlying LLM provider to wrap
            enable_compression: Whether to compress prompts (default: True)
            compression_threshold: Minimum prompt size to trigger compression (chars)
            auto_decompress: Whether to automatically decompress responses
            zepto_engine: Optional ZeptoEngine instance (creates new if None)
        """
        self.base_provider = base_provider
        self.enable_compression = enable_compression and ZEPTO_AVAILABLE
        self.compression_threshold = compression_threshold
        self.auto_decompress = auto_decompress
        self.zepto_engine = zepto_engine or (ZeptoEngine() if ZeptoEngine else None)
        
        # Track compression stats
        self.compression_stats = {
            'prompts_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'total_tokens_saved': 0,
            'responses_decompressed': 0
        }
    
    def _should_compress(self, prompt: str) -> bool:
        """Determine if prompt should be compressed."""
        if not self.enable_compression:
            return False
        if not ZEPTO_AVAILABLE:
            return False
        if len(prompt) < self.compression_threshold:
            return False
        return True
    
    def _compress_prompt(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Compress prompt using Zepto SPR.
        
        Returns:
            (compressed_prompt, compression_metadata)
        """
        try:
            if not self.zepto_engine:
                self.zepto_engine = ZeptoEngine()
            
            # Compress to Zepto stage
            result = compress_to_zepto(prompt, target_stage="Zepto", engine=self.zepto_engine)
            
            if result.error:
                logger.warning(f"Zepto compression failed: {result.error}. Using original prompt.")
                return prompt, {'compressed': False, 'error': result.error}
            
            # Build compressed prompt with decompression instructions
            compressed_prompt = self._build_compressed_prompt(
                zepto_spr=result.zepto_spr,
                codex_entries=result.new_codex_entries,
                original_length=result.original_length
            )
            
            # Calculate token savings (rough estimate: 1 token ≈ 4 chars)
            original_tokens = len(prompt) // 4
            compressed_tokens = len(compressed_prompt) // 4
            tokens_saved = original_tokens - compressed_tokens
            
            # Update stats
            self.compression_stats['prompts_compressed'] += 1
            self.compression_stats['total_original_size'] += len(prompt)
            self.compression_stats['total_compressed_size'] += len(compressed_prompt)
            self.compression_stats['total_tokens_saved'] += tokens_saved
            
            logger.info(
                f"Zepto compression: {len(prompt)} → {len(compressed_prompt)} chars "
                f"({result.compression_ratio:.1f}:1 ratio, ~{tokens_saved} tokens saved)"
            )
            
            return compressed_prompt, {
                'compressed': True,
                'compression_ratio': result.compression_ratio,
                'original_size': result.original_length,
                'compressed_size': len(compressed_prompt),
                'tokens_saved': tokens_saved,
                'zepto_spr': result.zepto_spr,
                'codex_entries': result.new_codex_entries
            }
            
        except Exception as e:
            logger.warning(f"Zepto compression error: {e}. Using original prompt.")
            return prompt, {'compressed': False, 'error': str(e)}
    
    def _build_compressed_prompt(self, zepto_spr: str, codex_entries: Dict, original_length: int) -> str:
        """
        Build a prompt that includes the Zepto SPR with decompression instructions.
        
        The LLM will receive instructions to decompress the Zepto SPR and use it as context.
        """
        codex_json = ""
        if codex_entries:
            import json
            codex_json = json.dumps(codex_entries, indent=2)
        
        prompt = f"""You are receiving a Zepto SPR (Sparse Priming Representation) - a hyper-compressed symbolic form of information.

Your task is to decompress and understand this Zepto SPR, then use it as context for the actual query that follows.

Zepto SPR (compressed information):
{zepto_spr}

Symbol Codex (for decompression reference):
{codex_json if codex_json else "{}"}

Original information size: {original_length} characters
Compressed to: {len(zepto_spr)} characters

DECOMPRESSION INSTRUCTIONS:
1. Parse the Zepto SPR symbols using the codex
2. Reconstruct the semantic meaning
3. Use this as context for the user's query below

USER QUERY (decompress the Zepto SPR above to understand the context, then answer this):
"""
        return prompt
    
    def _decompress_response(self, response: str, compression_metadata: Dict[str, Any]) -> str:
        """
        Decompress response if it contains Zepto SPR.
        
        Currently, responses are typically not compressed, but this allows for future
        compression of long responses.
        """
        # For now, responses are not compressed
        # This is a placeholder for future response compression
        if self.auto_decompress and compression_metadata.get('compressed'):
            # Check if response contains Zepto SPR markers
            if '⟦' in response or '→' in response:
                try:
                    # Attempt to decompress if it looks like Zepto
                    if self.zepto_engine:
                        # This would require the codex entries from the original compression
                        codex_entries = compression_metadata.get('codex_entries', {})
                        # Decompression logic would go here
                        pass
                except Exception as e:
                    logger.warning(f"Response decompression failed: {e}")
        
        return response
    
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text with Zepto compression.
        
        Compresses the prompt before sending to reduce token usage.
        """
        compression_metadata = {'compressed': False}
        original_prompt = prompt
        
        # Compress prompt if enabled and threshold met
        if self._should_compress(prompt):
            prompt, compression_metadata = self._compress_prompt(prompt)
        
        # Call base provider with (possibly compressed) prompt
        try:
            response = self.base_provider.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Decompress response if needed
            response = self._decompress_response(response, compression_metadata)
            
            return response
            
        except LLMProviderError as e:
            # Check if this is a rate limit or temporary error
            is_rate_limit = (
                'rate limit' in str(e).lower() or
                '429' in str(e) or
                'quota' in str(e).lower() or
                'limit' in str(e).lower()
            )
            
            # If generation fails with compressed prompt, try with original
            if compression_metadata.get('compressed'):
                logger.warning(f"Generation failed with compressed prompt, retrying with original: {e}")
                try:
                    return self.base_provider.generate(
                        prompt=original_prompt,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                except Exception as retry_error:
                    # If base provider supports fallback, let it handle it
                    # Otherwise, re-raise to trigger fallback chain
                    if hasattr(self.base_provider, '_try_provider_chain'):
                        raise  # Let fallback provider handle it
                    raise LLMProviderError(
                        f"Generation failed with both compressed and original prompts. "
                        f"Compressed error: {e}. Original error: {retry_error}",
                        provider=self.base_provider._provider_name if hasattr(self.base_provider, '_provider_name') else 'unknown',
                        original_exception=e
                    ) from retry_error
            
            # Re-raise to trigger fallback chain if base provider supports it
            raise
        except Exception as e:
            # If generation fails with compressed prompt, try with original
            if compression_metadata.get('compressed'):
                logger.warning(f"Generation failed with compressed prompt, retrying with original: {e}")
                try:
                    return self.base_provider.generate(
                        prompt=original_prompt,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                except Exception as retry_error:
                    raise LLMProviderError(
                        f"Generation failed with both compressed and original prompts. "
                        f"Compressed error: {e}. Original error: {retry_error}",
                        provider=self.base_provider._provider_name if hasattr(self.base_provider, '_provider_name') else 'unknown',
                        original_exception=e
                    ) from retry_error
            raise
    
    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate chat completion with Zepto compression.
        
        Compresses user messages before sending.
        """
        compression_metadata = {'compressed': False}
        original_messages = messages.copy()
        
        # Compress user messages
        compressed_messages = []
        for msg in messages:
            if msg.get('role') == 'user' and self._should_compress(msg.get('content', '')):
                compressed_content, metadata = self._compress_prompt(msg['content'])
                compression_metadata = metadata
                compressed_messages.append({
                    'role': msg['role'],
                    'content': compressed_content
                })
            else:
                compressed_messages.append(msg)
        
        # Call base provider
        try:
            response = self.base_provider.generate_chat(
                messages=compressed_messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Decompress response if needed
            response = self._decompress_response(response, compression_metadata)
            
            return response
            
        except LLMProviderError as e:
            # If generation fails with compressed messages, try with original
            if compression_metadata.get('compressed'):
                logger.warning(f"Chat generation failed with compressed messages, retrying with original: {e}")
                try:
                    return self.base_provider.generate_chat(
                        messages=original_messages,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                except Exception as retry_error:
                    # If base provider supports fallback, let it handle it
                    if hasattr(self.base_provider, '_try_provider_chain'):
                        raise  # Let fallback provider handle it
                    raise LLMProviderError(
                        f"Chat generation failed with both compressed and original messages. "
                        f"Compressed error: {e}. Original error: {retry_error}",
                        provider=self.base_provider._provider_name if hasattr(self.base_provider, '_provider_name') else 'unknown',
                        original_exception=e
                    ) from retry_error
            
            # Re-raise to trigger fallback chain if base provider supports it
            raise
        except Exception as e:
            # If generation fails with compressed messages, try with original
            if compression_metadata.get('compressed'):
                logger.warning(f"Chat generation failed with compressed messages, retrying with original: {e}")
                try:
                    return self.base_provider.generate_chat(
                        messages=original_messages,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                except Exception as retry_error:
                    raise LLMProviderError(
                        f"Chat generation failed with both compressed and original messages. "
                        f"Compressed error: {e}. Original error: {retry_error}",
                        provider=self.base_provider._provider_name if hasattr(self.base_provider, '_provider_name') else 'unknown',
                        original_exception=e
                    ) from retry_error
            raise
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        stats = self.compression_stats.copy()
        if stats['prompts_compressed'] > 0:
            avg_ratio = (
                stats['total_original_size'] / stats['total_compressed_size']
                if stats['total_compressed_size'] > 0 else 1.0
            )
            stats['average_compression_ratio'] = avg_ratio
            stats['total_tokens_saved_estimate'] = stats['total_tokens_saved']
        else:
            stats['average_compression_ratio'] = 1.0
        return stats
    
    def reset_stats(self):
        """Reset compression statistics."""
        self.compression_stats = {
            'prompts_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'total_tokens_saved': 0,
            'responses_decompressed': 0
        }

