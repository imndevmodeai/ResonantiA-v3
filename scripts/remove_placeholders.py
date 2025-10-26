import re

placeholder_files = [
    '/media/newbu/3626C55326C514B1/Happier/cursor_introducing_arche_and_imndevmode7.6.25.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_prime_yourself_as_archetype08.15.2025.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_arche_system_version_4_0_evoluti.08.24.2025.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_file_references_and_integration7.6.25.md',
    '/media/newbu/3626C55326C514B1/Happier/7.6.25cursor_prepare_arche_for_operation.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_understand_specifications_thorou.08.25.2025.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_locate_json_file_for_project_hap.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_making_it_as_above_so_below.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_notify_every_time_for_updates.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_prepare_arche_for_operation7.6.25.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_prime_the_protocols_for_collabor.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_prime_yourself_for_specification.9.5.25.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_prime_yourself_for_specification.9.9.25.md',
    '/media/newbu/3626C55326C514B1/Happier/cursor_prime_yourself_for_specification09.14.25existingcodeissue.md',
    '/media/newbu/3626C55326C514B1/Happier/backup_protocol_spr_correction_20250718_173138/ResonantiA_Protocol_v3.1-CA.md',
    '/media/newbu/3626C55326C514B1/Happier/protocol/ResonantiA_Protocol_v2.9.5.md',
    '/media/newbu/3626C55326C514B1/Happier/archemuliplied/cursor_review_orchestrator_and_scaffold08.20.2025.md',
    '/media/newbu/3626C55326C514B1/Happier/archemuliplied/tools/code_executor.py',
    '/media/newbu/3626C55326C514B1/Happier/core_workflows/6_specialized_protocols/resonant_autopoietic_genesis_protocol.json',
]

for file_path in placeholder_files:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        content = re.sub(r'(\.\.\.\s*existing code\s*\.\.\.|# \.\.\. existing code \.\.\.|// \.\.\. existing code \.\.\.|\/\* \.\.\. existing code \.\.\. \*\/)', '', content)

        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f'Processed {file_path}')
    except Exception as e:
        print(f'Error processing {file_path}: {e}')
