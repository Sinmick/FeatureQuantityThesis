#!/usr/bin/env python3
# extract_archives.py

import os
import zipfile
import tarfile
import gzip
import shutil
import csv
import json
import re
import base64
import statistics
import math
import asyncio
import datetime

# Define a tuple of file extensions
extensions = (
    # Python source and stubs
    ".py", ".pyw", ".pyi",
    # C/C++ source and header files (used in extensions)
    ".c", ".cpp", ".cc", ".cxx",
    ".h", ".hpp", ".hh", ".hxx",
    # Cython source files
    ".pyx", ".pxd",
    # Assembly files (rare but possible)
    ".s", ".asm",
    # Fortran source files (common in scientific computing)
    ".f", ".for", ".f77", ".f90", ".f95",
    # Rust source files (for Rust-based extensions)
    ".rs",
    # Shell scripts (often used in build processes)
    ".sh", ".bash", ".zsh",
    # Web assets (if applicable)
    ".js", ".mjs",
    # SQL scripts (if the package includes database scripts)
    ".sql"
)



def count_file_types(directory):
    """
    Counts the number of occurrences of specific file extensions in the given directory.

    Returns a dictionary where keys are file extensions and values are their counts.
    """
    file_types = [
        'bat', 'bz2', 'c', 'cert', 'conf', 'cpp', 'crt', 'css', 'csv', 'deb', 'erb', 'gemspec', 'gif', 'gz', 'h', 'html',
        'ico', 'ini', 'jar', 'java', 'jpg', 'js', 'json', 'key', 'm4v', 'markdown', 'md', 'pdf', 'pem', 'png', 'ps', 'py',
        'rb', 'rpm', 'rst', 'sh', 'svg', 'toml', 'ttf', 'txt', 'xml', 'yaml', 'yml', 'eot', 'exe', 'jpeg', 'properties',
        'sql', 'swf', 'tar', 'woff', 'woff2', 'aac', 'bmp', 'cfg', 'dcm', 'dll', 'doc', 'flac', 'flv', 'ipynb', 'm4a',
        'mid', 'mkv', 'mp3', 'mp4', 'mpg', 'ogg', 'otf', 'pickle', 'pkl', 'psd', 'pxd', 'pxi', 'pyc', 'pyx', 'r', 'rtf',
        'so', 'sqlite', 'tif', 'tp', 'wav', 'webp', 'whl', 'xcf', 'xz', 'zip', 'mov', 'wasm', 'webm'
    ]

    

    file_counts = {ext: 0 for ext in file_types}  # Initialize all file type counts to 0

    for dirpath, _, subfiles in os.walk(directory):
        for fname in subfiles:
            ext = fname.split('.')[-1].lower()  # Get file extension
            if ext in file_counts:
                file_counts[ext] += 1

    return file_counts


# Generalization function: transforms identifiers and strings
def generalize_text(text):

    return ''.join('a' if c.isalpha() else '1' if c.isdigit() else c for c in text)

# Function to compute homogeneous and heterogeneous identifiers and strings
def compute_homogeneous_heterogeneous(directory):
    """
    Computes counts for homogeneous and heterogeneous identifiers and strings
    for the entire package and separately for the setup.py file.
    """
    # Package-wide counts
    homogeneous_identifiers = 0
    heterogeneous_identifiers = 0
    homogeneous_strings = 0
    heterogeneous_strings = 0

    # Setup.py-specific counts
    setup_homogeneous_identifiers = 0
    setup_heterogeneous_identifiers = 0
    setup_homogeneous_strings = 0
    setup_heterogeneous_strings = 0

    # Regex patterns
    identifier_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')  # Matches Python-like identifiers
    string_pattern = re.compile(r'["\'](.*?)["\']')  # Matches anything inside quotes



    # Process all files
    for dirpath, _, subfiles in os.walk(directory):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Process identifiers
                    identifiers = identifier_pattern.findall(content)
                    for identifier in identifiers:
                        transformed = generalize_text(identifier)
                        unique_chars = set(transformed)
                        if len(unique_chars) == 1:
                            homogeneous_identifiers += 1
                        else:
                            heterogeneous_identifiers += 1

                    # Process strings
                    strings = string_pattern.findall(content)
                    for string in strings:
                        transformed = generalize_text(string)
                        unique_chars = set(transformed)
                        if len(unique_chars) == 1:
                            homogeneous_strings += 1
                        else:
                            heterogeneous_strings += 1

                    # If processing setup.py, store separate counts
                    if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                        for identifier in identifiers:
                            transformed = generalize_text(identifier)
                            unique_chars = set(transformed)
                            if len(unique_chars) == 1:
                                setup_homogeneous_identifiers += 1
                            else:
                                setup_heterogeneous_identifiers += 1

                        for string in strings:
                            transformed = generalize_text(string)
                            unique_chars = set(transformed)
                            if len(unique_chars) == 1:
                                setup_homogeneous_strings += 1
                            else:
                                setup_heterogeneous_strings += 1

            except (OSError, UnicodeDecodeError):
                pass  # Ignore unreadable files

    return {
        # Package-wide stats
        "homogeneous_identifiers": homogeneous_identifiers,
        "heterogeneous_identifiers": heterogeneous_identifiers,
        "homogeneous_strings": homogeneous_strings,
        "heterogeneous_strings": heterogeneous_strings,

        # Setup.py-specific stats
        "setup_homogeneous_identifiers": setup_homogeneous_identifiers,
        "setup_heterogeneous_identifiers": setup_heterogeneous_identifiers,
        "setup_homogeneous_strings": setup_homogeneous_strings,
        "setup_heterogeneous_strings": setup_heterogeneous_strings,
    }


# Function to compute Shannon entropy for a given text
def entropy(text):
    """Computes Shannon entropy of a given text."""
    if not text:
        return 0  # Avoid division by zero

    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1

    entropy = 0
    text_length = len(text)

    for count in freq.values():
        probability = count / text_length
        entropy -= probability * math.log2(probability)

    return entropy

# Function to compute entropy statistics separately for identifiers and strings
def compute_entropy_by_category(directory):
    """
    Computes entropy statistics separately for identifiers and strings in the entire package
    and separately for setup.py if present.
    """
    # Entropy lists for the full package
    identifier_entropies = []
    string_entropies = []

    # Entropy lists for setup.py only
    setup_identifier_entropies = []
    setup_string_entropies = []

    # Regular expressions
    identifier_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')  # Matches Python identifiers
    string_pattern = re.compile(r'["\'](.*?)["\']')  # Matches anything inside quotes


    # Process all files
    for dirpath, _, subfiles in os.walk(directory):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Extract identifiers and compute their entropy
                    identifiers = identifier_pattern.findall(content)
                    for identifier in identifiers:
                        entropy_value = entropy(identifier)
                        identifier_entropies.append(entropy_value)

                        # If processing setup.py, store separate entropy values
                        if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                            setup_identifier_entropies.append(entropy_value)

                    # Extract strings and compute their entropy
                    strings = string_pattern.findall(content)
                    for string in strings:
                        entropy_value = entropy(string)
                        string_entropies.append(entropy_value)

                        # If processing setup.py, store separate entropy values
                    if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                            setup_string_entropies.append(entropy_value)

            except (OSError, UnicodeDecodeError):
                pass  # Ignore unreadable files

    return {
        # Full package entropy stats
        "identifier_entropy_mean": statistics.mean(identifier_entropies) if identifier_entropies else 0,
        "identifier_entropy_std_dev": statistics.stdev(identifier_entropies) if len(identifier_entropies) > 1 else 0,
        "identifier_entropy_max": max(identifier_entropies) if identifier_entropies else 0,
        "identifier_entropy_q3": statistics.quantiles(identifier_entropies, n=4)[2] if len(identifier_entropies) >= 4 else max(identifier_entropies) if identifier_entropies else 0,

        "string_entropy_mean": statistics.mean(string_entropies) if string_entropies else 0,
        "string_entropy_std_dev": statistics.stdev(string_entropies) if len(string_entropies) > 1 else 0,
        "string_entropy_max": max(string_entropies) if string_entropies else 0,
        "string_entropy_q3": statistics.quantiles(string_entropies, n=4)[2] if len(string_entropies) >= 4 else max(string_entropies) if string_entropies else 0,

        # Setup.py-specific entropy stats
        "setup_identifier_entropy_mean": statistics.mean(setup_identifier_entropies) if setup_identifier_entropies else 0,
        "setup_identifier_entropy_std_dev": statistics.stdev(setup_identifier_entropies) if len(setup_identifier_entropies) > 1 else 0,
        "setup_identifier_entropy_max": max(setup_identifier_entropies) if setup_identifier_entropies else 0,
        "setup_identifier_entropy_q3": statistics.quantiles(setup_identifier_entropies, n=4)[2] if len(setup_identifier_entropies) >= 4 else max(setup_identifier_entropies) if setup_identifier_entropies else 0,

        "setup_string_entropy_mean": statistics.mean(setup_string_entropies) if setup_string_entropies else 0,
        "setup_string_entropy_std_dev": statistics.stdev(setup_string_entropies) if len(setup_string_entropies) > 1 else 0,
        "setup_string_entropy_max": max(setup_string_entropies) if setup_string_entropies else 0,
        "setup_string_entropy_q3": statistics.quantiles(setup_string_entropies, n=4)[2] if len(setup_string_entropies) >= 4 else max(setup_string_entropies) if setup_string_entropies else 0,
    }


# Function to count specific symbols in all files of a package
def count_symbols_in_package(directory):
    bracket_counts = []  # Stores counts of [] in each file
    equal_counts = []  # Stores counts of = in each file
    plus_counts = []  # Stores counts of + in each file
    
    for dirpath, _, subfiles in os.walk(directory):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    bracket_counts.append(content.count('[') + content.count(']'))
                    equal_counts.append(content.count('='))
                    plus_counts.append(content.count('+'))
            except (OSError, UnicodeDecodeError):
                pass
    
    # Function to compute statistics for a list of counts
    def compute_stats(counts):
        if not counts:
            return 0, 0, 0, 0  # Default values if no data
        return (
            statistics.mean(counts),
            statistics.stdev(counts) if len(counts) > 1 else 0,
            max(counts),
            statistics.quantiles(counts, n=4)[2] if len(counts) >= 4 else max(counts)  # Q3
        )
    
    return {
        "bracket_mean": compute_stats(bracket_counts)[0],
        "bracket_std_dev": compute_stats(bracket_counts)[1],
        "bracket_max": compute_stats(bracket_counts)[2],
        "bracket_q3": compute_stats(bracket_counts)[3],

        "equal_mean": compute_stats(equal_counts)[0],
        "equal_std_dev": compute_stats(equal_counts)[1],
        "equal_max": compute_stats(equal_counts)[2],
        "equal_q3": compute_stats(equal_counts)[3],

        "plus_mean": compute_stats(plus_counts)[0],
        "plus_std_dev": compute_stats(plus_counts)[1],
        "plus_max": compute_stats(plus_counts)[2],
        "plus_q3": compute_stats(plus_counts)[3],
    }


def extract_archives(directory, destination=None):
    """
    Extract .zip, .tar, and .gz archives found in `directory`.
    Extracts into `destination` if provided; otherwise, extracts into `directory`.
    Uses the password "infected" for password-protected zip files.
    """
    if destination is None:
        destination = directory
    os.makedirs(destination, exist_ok=True)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            continue
        # Check if it's a .zip
        if zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath, 'r') as z:
                try:
                    z.setpassword(b'infected')
                    z.extractall(destination)
                except RuntimeError as e:
                    print(f"[ZIP] Could not extract {filename} with password 'infected': {e}")
                else:
                    print(f"[ZIP] Extracted: {filename} -> {destination}")
        # Check if it's a .tar
        elif tarfile.is_tarfile(filepath):
            try:
                with tarfile.open(filepath, 'r:*') as t:
                    t.extractall(destination, filter=lambda ti, tar: ti if (not os.path.isabs(ti.name) and ".." not in ti.name.split(os.path.sep)) else None)
                print(f"[TAR] Extracted: {filename} -> {destination}")
            except (tarfile.TarError, OSError) as e:
                print(f"[TAR] Could not extract {filename}: {e}")
        # Check if it's a single-file .gz
        elif filename.endswith('.gz'):
            out_filepath = os.path.join(destination, filename[:-3])
            try:
                with gzip.open(filepath, 'rb') as f_in, open(out_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                print(f"[GZ] Extracted: {filename} -> {out_filepath}")
            except OSError as e:
                print(f"[GZ] Could not extract {filename}: {e}")




def is_base64_encoded(s):
    try:
        decoded = base64.b64decode(s, validate=True)
        return base64.b64encode(decoded).decode('utf-8') == s
    except Exception:
        return False

def get_total_ip(root_dir):
    total_ips = 0
    setup_ips = 0
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    for dirpath, subdirs, subfiles in os.walk(root_dir):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        total_ips += len(ip_pattern.findall(line))

                        # If processing setup.py, store separate counts
                        if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                            setup_ips += len(ip_pattern.findall(line))

            except (OSError, UnicodeDecodeError):
                pass

    return (
        total_ips, setup_ips
    )

import re

def get_total_base64(root_dir):
    setup_base64 = 0
    total_base64 = 0

    string_pattern = re.compile(r'["\'](.*?)["\']')  # match content inside quotes

    for dirpath, _, subfiles in os.walk(root_dir):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)

            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    strings = string_pattern.findall(content)

                    for s in strings:
                        if is_base64_encoded(s.strip()):
                            total_base64 += 1
                            if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                                setup_base64 += 1

            except (OSError, UnicodeDecodeError):
                pass

    return total_base64, setup_base64


def get_total_url(root_dir):
    total_urls = 0
    setup_urls = 0
    url_pattern = re.compile(r'https?://\S+')
    
    for dirpath, subdirs, subfiles in os.walk(root_dir):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        total_urls += len(url_pattern.findall(line))



                        # If processing setup.py, store separate counts
                        if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                            setup_urls += len(url_pattern.findall(line))

            except (OSError, UnicodeDecodeError):
                pass

    return (
        total_urls, setup_urls
    )

def get_total_tokens(root_dir, tokens):
    total_tokens = 0
    setup_tokens = 0

    for dirpath, subdirs, subfiles in os.walk(root_dir):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        total_tokens += sum(line.count(token) for token in tokens)

                        # If processing setup.py, store separate counts
                        if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                            setup_tokens += sum(line.count(token) for token in tokens)

            except (OSError, UnicodeDecodeError):
                pass

    return (
         total_tokens, setup_tokens
    )

 

def get_total_lines(root_dir):
    total_lines = 0
    total_words = 0
    setup_lines = 0
    setup_words = 0
    for dirpath, subdirs, subfiles in os.walk(root_dir):
        for fname in subfiles:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line_words = line.split()
                        total_lines += 1
                        total_words += len(line_words)

                        # If processing setup.py, store separate counts
                        if os.path.basename(fpath) in {"setup.py", "__init__.py", "__init__.pyi", "__init__"}:
                            setup_lines += 1
                            setup_words += len(line_words)

            except (OSError, UnicodeDecodeError):
                pass

    return (
        total_lines, total_words, setup_lines, setup_words
    )

def get_total_install_script_patterns(root_dir):

    pattern = re.compile(
        r'\b(?:'
        r'exec\s*\(\s*open\s*\('
        r'|subprocess\.run\s*\('
        r'|subprocess\.call\s*\('
        r'|\[\s*[\'"]pip[\'"]\s*,\s*[\'"]install[\'"]'
        r'|\[\s*[\'"]pip[\'"]\s*,\s*[\'"]download[\'"]'
        r'|python\s+setup\.py\s+install'
        r'|\[\s*[\'"]python[\'"]\s*,\s*[\'"]setup\.py[\'"]\s*,\s*[\'"]install[\'"]'
        r'|entry_points\s*='
        r'|scripts\s*='
        r')\b',
        re.IGNORECASE
    )
    total = 0
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    total += len(matches)
            except (OSError, UnicodeDecodeError):
                pass
    return total

dangerous_pattern = re.compile(
    r'\b(?:chmod\s+\+x|rm\s+-rf\s+/|apt-get\s+install|yum\s+install|brew\s+install|Makefile\s+install:|sudo\s+make\s+install|wget\s+http://|socat\s+exec:)\b',
    re.IGNORECASE
)

def get_total_dangerous_install_commands(root_dir):
    total = 0
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = dangerous_pattern.findall(content)
                    total += len(matches)
            except (OSError, UnicodeDecodeError):
                continue
    return total

async def record_setup_info_to_csv(directory, csv_path, token_file):
    """
    Gathers statistics for each package (top-level directory) inside 'directory'
    by aggregating data over the entire directory tree. For each package, a single row
    is written to the CSV with metrics such as total lines, total words, etc.
    """
    with open(token_file, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
        
    results = []
    # Loop over each top-level directory (each unzipped package)
    for pkg in os.listdir(directory):
        pkg_path = os.path.join(directory, pkg)
        if not os.path.isdir(pkg_path):
            continue
        

        total_counts, total_ip, total_url, total_base64, total_tokens, symbol_stats, entropy_stats, homogeneity_stats, file_type_counts, total_install_patterns, total_dangerous  = await asyncio.gather(
            asyncio.to_thread(get_total_lines, pkg_path),
            asyncio.to_thread(get_total_ip, pkg_path),
            asyncio.to_thread(get_total_url, pkg_path),
            asyncio.to_thread(get_total_base64, pkg_path),
            asyncio.to_thread(get_total_tokens, pkg_path, tokens),
            asyncio.to_thread(count_symbols_in_package, pkg_path),
            asyncio.to_thread(compute_entropy_by_category, pkg_path),
            asyncio.to_thread(compute_homogeneous_heterogeneous, pkg_path),
            asyncio.to_thread(count_file_types, pkg_path),
            asyncio.to_thread(get_total_install_script_patterns, pkg_path),
            asyncio.to_thread(get_total_dangerous_install_commands, pkg_path)
        )
        total_tokens, setup_tokens = total_tokens
        total_base64, setup_base64 = total_base64
        total_urls, setup_urls = total_url
        total_ips, setup_ips = total_ip
        total_lines, total_words, setup_lines, setup_words = total_counts
        #Aggregate statistics for the entire package directory
        #total_lines, total_words, total_tokens, total_urls, total_base64, total_ips, \
        #setup_lines, setup_words, setup_tokens, setup_urls, setup_base64, setup_ips = get_total_count(pkg_path)
        
        #symbol_stats = count_symbols_in_package(pkg_path)
        #entropy_stats = compute_entropy_by_category(pkg_path)
        #homogeneity_stats = compute_homogeneous_heterogeneous(pkg_path)
        #file_type_counts = count_file_types(pkg_path)
        
        results.append([
            pkg,
            total_lines, total_words, total_tokens, total_urls, total_base64, total_ips,
            symbol_stats["bracket_mean"], symbol_stats["bracket_std_dev"], symbol_stats["bracket_max"], symbol_stats["bracket_q3"],
            symbol_stats["equal_mean"], symbol_stats["equal_std_dev"], symbol_stats["equal_max"], symbol_stats["equal_q3"],
            symbol_stats["plus_mean"], symbol_stats["plus_std_dev"], symbol_stats["plus_max"], symbol_stats["plus_q3"],
            entropy_stats["identifier_entropy_mean"], entropy_stats["identifier_entropy_std_dev"], entropy_stats["identifier_entropy_max"], entropy_stats["identifier_entropy_q3"],
            entropy_stats["string_entropy_mean"], entropy_stats["string_entropy_std_dev"], entropy_stats["string_entropy_max"], entropy_stats["string_entropy_q3"],
            homogeneity_stats["homogeneous_identifiers"], homogeneity_stats["heterogeneous_identifiers"],
            homogeneity_stats["homogeneous_strings"], homogeneity_stats["heterogeneous_strings"],
            setup_lines, setup_words, setup_tokens, setup_urls, setup_base64, setup_ips,
            entropy_stats["setup_identifier_entropy_mean"], entropy_stats["setup_identifier_entropy_std_dev"],
            entropy_stats["setup_identifier_entropy_max"], entropy_stats["setup_identifier_entropy_q3"],
            entropy_stats["setup_string_entropy_mean"], entropy_stats["setup_string_entropy_std_dev"],
            entropy_stats["setup_string_entropy_max"], entropy_stats["setup_string_entropy_q3"],
            homogeneity_stats["setup_homogeneous_identifiers"], homogeneity_stats["setup_heterogeneous_identifiers"],
            homogeneity_stats["setup_homogeneous_strings"], homogeneity_stats["setup_heterogeneous_strings"], total_install_patterns, total_dangerous
        ] + list(file_type_counts.values()))
        
        print("Processed", pkg)
        
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "PackageName", "Total Lines", "Total Words", "Total Tokens", "Total URLs", "Total Base64", "Total IPs",
            "Bracket Mean", "Bracket Std Dev", "Bracket Max", "Bracket Q3",
            "Equal Mean", "Equal Std Dev", "Equal Max", "Equal Q3",
            "Plus Mean", "Plus Std Dev", "Plus Max", "Plus Q3",
            "Identifier Entropy Mean", "Identifier Entropy Std Dev", "Identifier Entropy Max", "Identifier Entropy Q3",
            "String Entropy Mean", "String Entropy Std Dev", "String Entropy Max", "String Entropy Q3",
            "Homogeneous Identifiers", "Heterogeneous Identifiers", "Homogeneous Strings", "Heterogeneous Strings",
            "Setup Total Lines", "Setup Total Words", "Setup Total Tokens", "Setup Total URLs", "Setup Total Base64", "Setup Total IPs",
            "Setup Identifier Entropy Mean", "Setup Identifier Entropy Std Dev", "Setup Identifier Entropy Max", "Setup Identifier Entropy Q3",
            "Setup String Entropy Mean", "Setup String Entropy Std Dev", "Setup String Entropy Max", "Setup String Entropy Q3",
            "Setup Homogeneous Identifiers", "Setup Heterogeneous Identifiers", "Setup Homogeneous Strings", "Setup Heterogeneous Strings", "Total Install Script in .py", "Total Dangerous Install Commands Count"
        ] + [ext.upper() + " Count" for ext in file_type_counts.keys()])
        
        for row in results:
            writer.writerow(row)
            
    print("Results saved to", csv_path)

if __name__ == "__main__":
    startime = datetime.datetime.now()
    source_dir = r"C:\\Users\\Mikael Laptop\\MaliciousPackages"
    output_dir = r"C:\\Users\\Mikael Laptop\\Extraction\\ExtractedMaliciousPackages"
    token_file = r"C:\\Users\\Mikael Laptop\\Extraction\\dangerous_tokens.json"
    csv_output_path = os.path.join(output_dir, "dataset.csv")
    extract_archives(source_dir, output_dir)

    asyncio.run(record_setup_info_to_csv(output_dir, csv_output_path, token_file))
    endtime = datetime.datetime.now()
    print(f"Starttid: {startime} Sluttid: {endtime}")

