# HashReveal

A fast, efficient, and memory-safe hash cracking tool designed to work seamlessly with large wordlists (like **SecLists**). HashReveal utilizes a pre-computed hash mapping strategy for instantaneous lookups, avoiding RAM exhaustion common with massive dictionaries.

---

## Features
- **Memory Efficient**: Reads wordlists line-by-line during generation, avoiding RAM crashes.
- **Pre-computation Engine**: Pre-calculates hashes (MD5, SHA1, SHA224, SHA256, SHA384, SHA512) for lightning-fast cracking later.
- **Sleek TUI**: An interactive, Catppuccin-themed terminal dashboard for easy navigation.
- **SecLists Integrated**: Built specifically to reside within and utilize the SecLists `Passwords/Common-Credentials` directory.

---

## Prerequisites
Ensure you have Python 3 installed. The tool relies on the `pyfiglet` library for ASCII banners and the built-in `curses` and `hashlib` libraries.

---

## Installation & Setup

### 1. Navigate to the Directory
Ensure the scripts are placed inside your `SecLists` directory.
```bash
cd SecLists
```

### 2. Set Up the Virtual Environment
It is highly recommended to run this inside an isolated virtual environment.
```bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install pyfiglet
```

---

## Usage

### Step 1: Generate Hash Files (Crucial First Step)
Before cracking, you **must** generate the corresponding hash files for your wordlists. This script reads the wordlists in `Passwords/Common-Credentials` and generates separated `.txt` files for MD5, SHA1, SHA256, etc.

```bash
python3 hash_generator.py
```
> **Note:** This process might take some time depending on the size of your wordlists, but it only needs to be executed once per wordlist.

---

### Step 2: Crack Hashes
Choose the interface that suits you best.

#### Option A: The Interactive TUI (Recommended)
Launch the sleek dashboard to select algorithms, wordlists, and input target hashes interactively.
```bash
python3 hach_tui.py
```

#### Option B: The Standard CLI
A simple, prompt-based interface optimized for the `Passwords/Common-Credentials` structure.
```bash
python3 hachmk.py
```

#### Option C: The Manual CLI (External Wordlists)
If you want to manually provide an absolute path to a wordlist.
```bash
python3 hach.py
```

---

## Directory Structure
After setup and running the generator, your structure will look like this:

```text
SecLists/
├── venv/                 # Python Virtual Environment
├── hash_generator.py     # Pre-computes hashes
├── hach_tui.py           # Interactive Dashboard
├── hachmk.py             # Standard CLI tool
├── hach.py               # Manual CLI tool
└── Passwords/
    └── Common-Credentials/
        ├── 10k-most-common.txt
        ├── 10k-most-common_MD5.txt    (Generated)
        ├── 10k-most-common_SHA256.txt (Generated)
        └── ...
```

---

## Supported Algorithms
- MD5
- SHA-1
- SHA-224
- SHA-256
- SHA-384
- SHA-512
