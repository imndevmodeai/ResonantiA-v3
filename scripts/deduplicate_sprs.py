import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

SPR_JSON_FILE = 'knowledge_graph/spr_definitions_tv.json'

def remove_duplicate_spr_ids(filepath: str):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            spr_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: SPR definitions file not found at {filepath}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filepath}: {e}")
        return

    unique_spr_ids = set()
    deduplicated_sprs = []
    duplicate_count = 0

    for spr in spr_data:
        spr_id = spr.get('spr_id')
        if spr_id:
            if spr_id not in unique_spr_ids:
                unique_spr_ids.add(spr_id)
                deduplicated_sprs.append(spr)
            else:
                logger.warning(f"Duplicate SPR ID found and removed: '{spr_id}'")
                duplicate_count += 1
        else:
            logger.warning(f"Entry without 'spr_id' found and skipped: {spr}")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(deduplicated_sprs, f, indent=2)
        logger.info(f"Successfully removed {duplicate_count} duplicate SPR entries from {filepath}.")
        logger.info(f"Total unique SPRs remaining: {len(deduplicated_sprs)}")
    except IOError as e:
        logger.error(f"Error writing deduplicated SPRs to {filepath}: {e}")

if __name__ == "__main__":
    remove_duplicate_spr_ids(SPR_JSON_FILE) 