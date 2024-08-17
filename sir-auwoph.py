import os
import sys
import re
import argparse
from colorama import init, Fore, Style
from convert_html import generate_report

init(autoreset=True)

def get_patterns(file_path):
    patterns = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                pattern = line.strip()
                if pattern:
                    patterns.append(pattern)
    except FileNotFoundError:
        print(f"{Fore.RED}Error:{Style.RESET_ALL} File not found: {file_path}")
        sys.exit(1)
    return patterns

def read_files(patterns, plugin_slug, rules_name):
    if not plugin_slug:
        print(f"{Fore.RED}Error:{Style.RESET_ALL} Plugin folder is required")
        sys.exit(1)

    output_dir = 'results'
    plugin_output = os.path.join(output_dir, plugin_slug, 'vuln', rules_name)

    file_count = 0
    code_count = 0

    plugin_path = os.path.join('plugins', plugin_slug)

    for root, dirs, files in os.walk(plugin_path):
        for file in files:
            if file.endswith('.php'):
                file_path = os.path.join(root, file)
                
                output_file_path = os.path.join(plugin_output, file.replace('.php', '.txt'))

                file_written = False
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    for num, line in enumerate(f, 1):
                        for regex in patterns:
                            if re.search(regex, line):
                                if not os.path.exists(plugin_output):
                                    os.makedirs(plugin_output)
                                with open(output_file_path, 'a', encoding='utf-8') as outf:
                                    if not file_written:
                                        outf.write(f"[File] {file} ({file_path})\n\n")
                                        file_written = True
                                    outf.write(f"[{num}] {line.strip()}\n")
                                    code_count += 1
                
                if file_written:
                    file_count += 1

    if file_count > 0 or code_count > 0:
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Scanning for {Fore.RED}{rules_name.upper()}{Style.RESET_ALL} Completed! Found: {Fore.RED}{file_count}{Style.RESET_ALL} files and {Fore.RED}{code_count}{Style.RESET_ALL} code")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WordPress Plugin Scanner')
    parser.add_argument('rules', help='The rules file to scan for vulnerabilities (e.g., sqli.txt)')

    args = parser.parse_args()
    rules_file = args.rules

    # Ambil nama file rules tanpa ekstensi
    rules_name = os.path.splitext(os.path.basename(rules_file))[0]

    # Ambil patterns dari file rules yang diinput
    patterns = get_patterns(rules_file)

    plugins_dir = 'plugins'

    # Loop melalui setiap folder dalam direktori plugins
    for plugin_slug in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, plugin_slug)
        if os.path.isdir(plugin_path):
            print(f"{Fore.BLUE}[i]{Style.RESET_ALL} Scanning plugin: {plugin_slug}")
            read_files(patterns, plugin_slug, rules_name)
            generate_report()

    print(f"{Fore.GREEN}[Done]{Style.RESET_ALL} Output files are in the {Fore.BLUE}'results'{Style.RESET_ALL} directory.")
