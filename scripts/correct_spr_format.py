import json
import os
import re
import logging
import copy
from typing import Dict, Any, List, Optional, Tuple, Union

# Set up logging for the script
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define the path to the SPR definitions file
KNOWLEDGE_GRAPH_DIR = 'knowledge_graph'
SPR_JSON_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, 'spr_definitions_tv.json')

class SPRFormatter:
    """
    Helper class to apply and validate SPR Guardian Points format.
    Contains the exact is_spr logic copied from spr_manager.py (lines 276-339)
    and methods to attempt reformatting.
    """
    def is_spr(self, text: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Checks if a given text string strictly matches the SPR format (Guardian Points).
        An SPR consists of one or more words separated by single spaces.
        Each word must:
        - Be at least 3 characters long.
        - Start with an uppercase letter (if alphabetic, otherwise alphanumeric).
        - End with an uppercase letter (if alphabetic, otherwise alphanumeric).
        - Have all middle characters as lowercase letters (if any).
        The overall SPR phrase must:
        - Be at least 3 characters long.
        - Not have leading or trailing spaces.
        - Not have multiple spaces between words.
        """
        if not text or not isinstance(text, str):
            return False, "SPR text must be a non-empty string."

        if text.strip() != text:
            return False, f"SPR '{text}': Must not have leading or trailing spaces."

        if "  " in text: # Check for multiple spaces between words
            return False, f"SPR '{text}': Must not contain multiple spaces between words."

        words = text.split(' ')
        if not words:
            return False, "SPR text split into no words."
        
        # Check overall length of the original text string. The rule "Be at least 3 characters long"
        # appears under "Each word must", but also applies to the overall SPR phrase.
        if len(text) < 3:
            return False, f"SPR '{text}': Overall text length must be at least 3 characters."

        for i, word in enumerate(words):
            if not word:
                 return False, f"SPR '{text}': Contains an empty word segment at word index {i}."
            
            if len(word) < 3: # Explicitly check word length here
                return False, f"SPR '{text}': Word '{word}' (index {i}): Must be at least 3 characters long."

            first_char = word[0]
            last_char = word[-1]
            middle_chars = word[1:-1]

            # Rule: First character of word
            if not first_char.isalnum():
                return False, f"SPR '{text}': Word '{word}' (index {i}): First character '{first_char}' must be alphanumeric."
            if first_char.isalpha() and not first_char.isupper():
                return False, f"SPR '{text}': Word '{word}' (index {i}): First alphabetic character '{first_char}' must be uppercase."

            # Rule: Last character of word
            if not last_char.isalnum():
                return False, f"SPR '{text}': Word '{word}' (index {i}): Last character '{last_char}' must be alphanumeric."
            if last_char.isalpha() and not last_char.isupper():
                return False, f"SPR '{text}': Word '{word}' (index {i}): Last alphabetic character '{last_char}' must be uppercase."

            # Rule: Middle characters of word (if any)
            if middle_chars:
                for char_idx, char_val in enumerate(middle_chars):
                    if char_val.isalpha() and not char_val.islower():
                        return False, f"SPR '{text}': Word '{word}' (index {i}): Middle alphabetic character '{char_val}' (at char index {char_idx + 1} of word) must be lowercase."
                    elif not char_val.isalnum() and char_val != ' ':
                        # The ' ' check here is likely for if the word itself contains spaces internally
                        # which is unlikely after split(' '), but to match source logic.
                        return False, f"SPR '{text}': Word '{word}' (index {i}): Middle character '{char_val}' (at char index {char_idx + 1} of word) must be alphanumeric or a space."
                    
        return True, None

    def reformat_spr_id(self, spr_id: str) -> Tuple[str, Optional[str]]:
        original_spr_id = spr_id
        
        # 1. Clean up spaces. `is_spr` checks for leading/trailing/multiple spaces in final string.
        # We need to process words based on split, then re-join with single spaces.
        words = [word for word in spr_id.split(' ') if word] # Remove empty strings from split

        if not words:
            return original_spr_id, "No valid words found after splitting and cleaning spaces."

        reformatted_words = []

        for word in words:
            # Check rule: Contain only alphanumeric characters (before reformatting attempt)
            if not word.isalnum():
                return original_spr_id, f"Original word \'{word}\' contains non-alphanumeric characters. Cannot reformat to SPR."

            # Check rule: Be at least 3 characters long.
            if len(word) < 3:
                return original_spr_id, f"Original word \'{word}\' is less than 3 characters long. Cannot reformat to SPR."
            
            # Apply casing rules only if the word contains any alphabetic characters
            if any(c.isalpha() for c in word):
                # Strict rule: If word has letters, it MUST start and end with an alphabetic character
                # and these will be forced to uppercase. If not, it cannot conform.
                if not word[0].isalpha() or not word[-1].isalpha():
                    return original_spr_id, f"Original word \'{word}\' contains letters but does not start/end with an alphabetic character. Cannot conform to SPR format."
                
                reformatted_word_chars = [word[0].upper()] # Force first char to uppercase
                for char in word[1:-1]: # Middle characters
                    if char.isalpha():
                        reformatted_word_chars.append(char.lower()) # Force middle alpha to lowercase
                    else:
                        reformatted_word_chars.append(char) # Keep non-alpha as is
                
                if len(word) > 1: # Add last character if it exists
                    reformatted_word_chars.append(word[-1].upper()) # Force last char to uppercase
                
                reformatted_word = "".join(reformatted_word_chars)
            else:
                # Word contains only numbers (e.g., "123"). No casing reformatting needed.
                reformatted_word = word
            
            reformatted_words.append(reformatted_word)
        
        # Reconstruct the full SPR ID with single spaces.
        # This implicitly handles the "no multiple spaces" and "no leading/trailing spaces" rules
        # when combined with the is_spr final check.
        final_reformatted_id = ' '.join(reformatted_words)
        
        # Final validation of the entire reformatted string using the strict is_spr method.
        # This is crucial to catch any edge cases the reformatting might have missed,
        # or if the original was simply unfixable into a valid SPR.
        is_valid, validation_msg = self.is_spr(final_reformatted_id)
        if not is_valid:
            return original_spr_id, f"Reformatted SPR \'{final_reformatted_id}\' failed final validation: {validation_msg}"
        
        return final_reformatted_id, None

def main():
    formatter = SPRFormatter()
    
    if not os.path.exists(SPR_JSON_FILE):
        logger.error(f"SPR definition file not found: {SPR_JSON_FILE}. Cannot proceed.")
        return

    original_sprs = []
    try:
        with open(SPR_JSON_FILE, 'r', encoding='utf-8') as f:
            original_sprs = json.load(f)
        if not isinstance(original_sprs, list):
            logger.error(f"SPR file {SPR_JSON_FILE} does not contain a valid JSON list. Exiting.")
            return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from SPR file {SPR_JSON_FILE}: {e}. Exiting.")
        return
    except IOError as e:
        logger.error(f"Error reading SPR file {SPR_JSON_FILE}: {e}. Exiting.")
        return

    updated_sprs = []
    reformatted_count = 0
    skipped_count = 0

    for idx, spr_def in enumerate(original_sprs):
        if not isinstance(spr_def, dict):
            logger.warning(f"Skipping entry at index {idx} due to invalid structure (not a dict).")
            updated_sprs.append(spr_def) # Keep original, but warn
            skipped_count += 1
            continue
            
        original_id = spr_def.get("spr_id")
        if not original_id or not isinstance(original_id, str):
            logger.warning(f"Skipping entry at index {idx} due to missing or invalid 'spr_id'.")
            updated_sprs.append(spr_def) # Keep original, but warn
            skipped_count += 1
            continue

        is_valid_initial, initial_reason = formatter.is_spr(original_id)
        if is_valid_initial:
            logger.info(f"SPR '{original_id}' (index {idx}) already valid. No reformat needed.")
            updated_sprs.append(spr_def)
        else:
            logger.info(f"SPR '{original_id}' (index {idx}) is invalid: {initial_reason}. Attempting reformat...")
            reformatted_id, reformat_reason = formatter.reformat_spr_id(original_id)
            
            if reformatted_id:
                spr_def["spr_id"] = reformatted_id
                # Also update the 'term' field if it matches the original spr_id, to keep consistent
                # This is a heuristic based on the 'term' often being a human-readable version of spr_id
                if spr_def.get("term") == original_id:
                    spr_def["term"] = reformatted_id 
                updated_sprs.append(spr_def)
                reformatted_count += 1
                logger.info(f"Successfully reformatted '{original_id}' to '{reformatted_id}'.")
            else:
                logger.error(f"Failed to reformat SPR '{original_id}' (index {idx}): {reformat_reason}. Keeping original invalid entry.")
                updated_sprs.append(spr_def) # Keep original if reformat fails
                skipped_count += 1

    try:
        with open(SPR_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(updated_sprs, f, indent=2, ensure_ascii=False)
        logger.info(f"Process complete. Reformatted {reformatted_count} SPRs. Skipped/kept original for {skipped_count} invalid entries.")
        logger.info(f"Updated SPR definitions saved to {SPR_JSON_FILE}.")
    except IOError as e:
        logger.error(f"Error writing updated SPR file {SPR_JSON_FILE}: {e}. Changes not saved.")
    except Exception as e_save:
        logger.error(f"Unexpected error saving updated SPRs: {e_save}", exc_info=True)

if __name__ == "__main__":
    main() 