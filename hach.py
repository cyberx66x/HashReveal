import hashlib
import sys
import pyfiglet
import os

ascii_banner = pyfiglet.figlet_format("Hash Cracker")
print(ascii_banner)

print("Algorithms available: MD5 | SHA1 | SHA224 | SHA256 | SHA384 | SHA512")

hash_type = input("What's the hash type? ").strip().upper()
wordlist_location = input("Enter wordlist location: ").strip()
target_hash = input("Enter hash: ").strip().lower()

if hash_type not in ["MD5", "SHA1", "SHA224", "SHA256", "SHA384", "SHA512"]:
    print("[-] Invalid hash algorithm. Please choose from the given options.")
    sys.exit()

if not os.path.exists(wordlist_location):
    print("[-] Wordlist file not found!")
    sys.exit()

print(f"[*] Starting crack for {target_hash} using {hash_type}...")

found = False
try:
    with open(wordlist_location, "r", encoding="utf-8", errors="ignore") as file:
        for word in file:
            word = word.strip()
            if not word: continue
            
            if hash_type == "MD5":
                hashed = hashlib.md5(word.encode('utf-8')).hexdigest()
            elif hash_type == "SHA1":
                hashed = hashlib.sha1(word.encode('utf-8')).hexdigest()
            elif hash_type == "SHA224":
                hashed = hashlib.sha224(word.encode('utf-8')).hexdigest()
            elif hash_type == "SHA256":
                hashed = hashlib.sha256(word.encode('utf-8')).hexdigest()
            elif hash_type == "SHA384":
                hashed = hashlib.sha384(word.encode('utf-8')).hexdigest()
            elif hash_type == "SHA512":
                hashed = hashlib.sha512(word.encode('utf-8')).hexdigest()
                
            if target_hash == hashed:
                print(f"\n\033[1;32m[+] HASH FOUND: {word} \033[0m\n")
                found = True
                break
except Exception as e:
    print(f"[-] Error reading file: {e}")

if not found:
    print("[-] Hash not found in the provided wordlist.")