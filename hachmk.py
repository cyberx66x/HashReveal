import hashlib
import sys
import pyfiglet
import os

ascii_banner = pyfiglet.figlet_format("mk")
print(ascii_banner)

print("Algorithms available: MD5 | SHA1 | SHA224 | SHA256 | SHA384 | SHA512")

# المسار الجديد بعد النقل لداخل SecLists
WORDLIST_PATH = "Passwords/Common-Credentials"

if not os.path.exists(WORDLIST_PATH):
    print(f"[-] Directory not found: {WORDLIST_PATH}")
    sys.exit()

print("\nAvailable Wordlists:\n")
for file in sorted(os.listdir(WORDLIST_PATH)):
    if os.path.isfile(os.path.join(WORDLIST_PATH, file)):
        # يمكن إخفاء ملفات الهاشات المولدة من القائمة لتسهيل العرض
        if not any(file.endswith(f"_{a}.txt") for a in ["MD5", "SHA1", "SHA224", "SHA256", "SHA384", "SHA512"]):
            print(" -", file)
print()

hash_type = input("What's the hash type? ").strip().upper()
wordlist_name = input("Enter wordlist name: ").strip()
target_hash = input("Enter hash: ").strip().lower()

wordlist_location = os.path.join(WORDLIST_PATH, wordlist_name)

if hash_type not in ["MD5", "SHA1", "SHA224", "SHA256", "SHA384", "SHA512"]:
    print("[-] Invalid hash algorithm!")
    sys.exit()

if not os.path.exists(wordlist_location):
    print("[-] Wordlist file not found!")
    sys.exit()

found = False
print("[*] Starting crack...")
try:
    with open(wordlist_location, "r", encoding="utf-8", errors="ignore") as file:
        for word in file:
            word = word.strip()
            if not word:
                continue

            if hash_type == "MD5":
                hashed = hashlib.md5(word.encode()).hexdigest()
            elif hash_type == "SHA1":
                hashed = hashlib.sha1(word.encode()).hexdigest()
            elif hash_type == "SHA224":
                hashed = hashlib.sha224(word.encode()).hexdigest()
            elif hash_type == "SHA256":
                hashed = hashlib.sha256(word.encode()).hexdigest()
            elif hash_type == "SHA384":
                hashed = hashlib.sha384(word.encode()).hexdigest()
            elif hash_type == "SHA512":
                hashed = hashlib.sha512(word.encode()).hexdigest()

            if hashed == target_hash:
                print(f"\n\033[1;32m[+] HASH FOUND: {word}\033[0m")
                found = True
                break
except Exception as e:
    print(f"[-] Error: {e}")

if not found:
    print("\n[-] Hash not found in the wordlist.")