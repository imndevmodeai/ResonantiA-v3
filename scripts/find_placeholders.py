import os

def find_placeholder_files(root_dir, output_file):
    with open(output_file, 'w') as out_f:
        for dirpath, _, filenames in os.walk(root_dir):
            if 'outputs' in dirpath or 'nextjs-chat_backup_quarantine' in dirpath:
                continue
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as in_f:
                        if '[[PLACEHOLDER]]' in in_f.read():
                            out_f.write(f"{filepath}\n")
                except Exception:
                    continue

if __name__ == "__main__":
    find_placeholder_files('.', 'placeholder_files.txt')





