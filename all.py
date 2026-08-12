import os

def merge_wordlists():
    base_dir = "Passwords/Common-Credentials"
    output_file = "all.txt"
    output_path = os.path.join(base_dir, output_file)

    if not os.path.exists(base_dir):
        print(f"[-] Directory not found: {base_dir}")
        return

    unique_words = set()

    print("[*] Reading files and extracting unique words...")
    
    # قائمة بأنواع الهاش لتخطي الملفات المولدة
    hash_suffixes = ["_MD5.txt", "_SHA1.txt", "_SHA224.txt", "_SHA256.txt", "_SHA384.txt", "_SHA512.txt"]

    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)
        
        # التأكد أنه ملف، وليس مجلد، وتخطي ملف المخرجات وملفات الهاشات
        if os.path.isfile(file_path) and filename != output_file and not any(filename.endswith(suf) for suf in hash_suffixes):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                    for line in infile:
                        word = line.strip()
                        if word:
                            unique_words.add(word)
            except Exception as e:
                print(f"[-] Error reading {filename}: {e}")

    print(f"[*] Writing {len(unique_words)} unique words to {output_file}...")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for word in unique_words:
                outfile.write(word + '\n')
        print(f"[+] Successfully created {output_path}")
    except Exception as e:
        print(f"[-] Error writing to {output_file}: {e}")

if __name__ == "__main__":
    merge_wordlists()