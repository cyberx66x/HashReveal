#!/usr/bin/env python3

import os
import sys
import curses
import hashlib
import threading
import queue
import time

LOGO = [
    " ██╗  ██╗ █████╗ ███████╗██╗  ██╗██████╗ ███████╗██╗   ██╗███████╗█████╗ ██╗     ",
    " ██║  ██║██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██║     ",
    " ███████║███████║███████╗███████║██████╔╝█████╗  ██║   ██║█████╗  ███████║██║     ",
    " ██╔══██║██╔══██║╚════██║██╔══██║██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██║██║     ",
    " ██║  ██║██║  ██║███████║██║  ██║██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║███████╗",
    " ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝"
]

DIRECTORY = "Passwords/Common-Credentials"

HASH_ALGORITHMS = {
    "MD5": hashlib.md5,
    "SHA1": hashlib.sha1,
    "SHA224": hashlib.sha224,
    "SHA256": hashlib.sha256,
    "SHA384": hashlib.sha384,
    "SHA512": hashlib.sha512
}

def setup_catppuccin_colors():
    curses.use_default_colors()
    try:
        if curses.can_change_color():
            def set_hex(col_id, hex_code):
                h = hex_code.lstrip('#')
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                curses.init_color(col_id, int(r*1000/255), int(g*1000/255), int(b*1000/255))

            BLUE = 200; set_hex(BLUE, "#89b4fa")
            MAUVE = 201; set_hex(MAUVE, "#cba6f7")
            GREEN = 202; set_hex(GREEN, "#a6e3a1")
            PEACH = 203; set_hex(PEACH, "#fab387")
            RED = 204; set_hex(RED, "#f38ba8")
            SURFACE1 = 205; set_hex(SURFACE1, "#45475a")
            OVERLAY0 = 206; set_hex(OVERLAY0, "#6c7086")
            BASE = 207; set_hex(BASE, "#1e1e2e")

            curses.init_pair(1, MAUVE, -1)
            curses.init_pair(2, GREEN, -1)
            curses.init_pair(3, PEACH, -1)
            curses.init_pair(4, BLUE, -1)
            curses.init_pair(5, OVERLAY0, -1)
            curses.init_pair(6, BASE, BLUE)
            curses.init_pair(7, RED, SURFACE1)
            curses.init_pair(8, BLUE, -1)
            curses.init_pair(9, PEACH, SURFACE1)
            curses.init_pair(10, BASE, GREEN)
        else:
            raise Exception()
    except:
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_BLUE, -1)
        curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN)

def draw_logo(stdscr, start_y, max_x):
    for i, line in enumerate(LOGO):
        x = max(0, (max_x - len(line)) // 2)
        try:
            stdscr.addstr(start_y + i, x, line[:max_x-1], curses.color_pair(8) | curses.A_BOLD)
        except curses.error:
            pass
    return start_y + len(LOGO) + 2

def process_files(selected_files, log_queue, status):
    for filename in selected_files:
        input_path = os.path.join(DIRECTORY, filename)
        base_name, ext = os.path.splitext(filename)
        
        log_queue.put(f"[*] Starting to process: {filename} ...")
        
        output_files = {}
        try:
            for algo in HASH_ALGORITHMS.keys():
                out_name = f"{base_name}_{algo}{ext}"
                out_path = os.path.join(DIRECTORY, out_name)
                output_files[algo] = open(out_path, 'w', encoding='utf-8')
            
            line_count = 0
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
                for line in infile:
                    word = line.strip()
                    if not word:
                        continue
                    
                    for algo, func in HASH_ALGORITHMS.items():
                        hashed_word = func(word.encode('utf-8')).hexdigest()
                        output_files[algo].write(hashed_word + '\n')
                        
                    line_count += 1
                    
                    if line_count % 1000 == 0:
                        log_queue.put(f"  -> [{filename}] {line_count} lines hashed...")
                        
            log_queue.put(f"[+] Finished {filename} (Total: {line_count} lines)")
            
        except Exception as e:
            log_queue.put(f"[-] Error processing {filename}: {e}")
        finally:
            for f in output_files.values():
                f.close()
    
    log_queue.put("[*] All selected files have been successfully processed!")
    status['is_processing'] = False

def run_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()

    base_dir = DIRECTORY
    if not os.path.exists(base_dir):
        base_dir = "."

    try:
        hash_suffixes = [f"_{algo}.txt" for algo in HASH_ALGORITHMS.keys()]
        files = []
        for f in os.listdir(base_dir):
            if os.path.isfile(os.path.join(base_dir, f)):
                if not any(f.endswith(suf) for suf in hash_suffixes):
                    files.append(f)
        files.sort()
    except Exception:
        files = []

    if not files:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        draw_logo(stdscr, 2, max_x)
        msg = " [!] No valid wordlists found to process. "
        stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg, curses.color_pair(7) | curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()
        return

    selected = [False] * len(files)
    highlight = 0
    offset = 0

    # File Selection UI
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        logo_bottom = draw_logo(stdscr, 1, max_x)
        start_y = logo_bottom + 1
        
        stdscr.addstr(start_y, 2, " === Hash Generator: Select Wordlists ===", curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(start_y + 1, 2, " Controls: [UP/DOWN] Navigate | [SPACE] Toggle | [a] Select All | [ENTER] Start", curses.color_pair(5))
        
        max_display = max_y - start_y - 3
        for i in range(max_display):
            idx = offset + i
            if idx >= len(files): break
            
            if idx == highlight:
                stdscr.attron(curses.A_REVERSE)
            
            prefix = "[*]" if selected[idx] else "[ ]"
            color = curses.color_pair(2) if selected[idx] else curses.color_pair(5)
            
            display_text = f" {prefix} {files[idx]} "
            stdscr.addstr(start_y + 3 + i, 4, display_text[:max_x-6], color)
            
            if idx == highlight:
                stdscr.attroff(curses.A_REVERSE)
        
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == curses.KEY_UP and highlight > 0:
            highlight -= 1
        elif ch == curses.KEY_DOWN and highlight < len(files) - 1:
            highlight += 1
        elif ch == ord(' '):
            selected[highlight] = not selected[highlight]
        elif ch in (ord('a'), ord('A')):
            all_sel = all(selected)
            selected = [not all_sel] * len(files)
        elif ch in (10, 13):
            if any(selected):
                break
        
        if highlight < offset: offset = highlight
        if highlight >= offset + max_display: offset = highlight - max_display + 1

    selected_files = [files[i] for i in range(len(files)) if selected[i]]
    
    # Threading and Queue Setup
    log_queue = queue.Queue()
    status = {'is_processing': True}
    
    t = threading.Thread(target=process_files, args=(selected_files, log_queue, status), daemon=True)
    t.start()

    # Live Logs UI
    logs = []
    while status['is_processing'] or not log_queue.empty():
        while not log_queue.empty():
            logs.append(log_queue.get())
        
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        logo_bottom = draw_logo(stdscr, 1, max_x)
        start_y = logo_bottom + 1
        
        stdscr.addstr(start_y, 2, " === Live Processing Logs ===", curses.color_pair(3) | curses.A_BOLD)
        
        visible_log_lines = max_y - start_y - 4
        display_logs = logs[-visible_log_lines:] if len(logs) > visible_log_lines else logs
        
        for i, log in enumerate(display_logs):
            color = curses.color_pair(5)
            if "[+]" in log or "[*] All" in log: color = curses.color_pair(2) | curses.A_BOLD
            elif "[*]" in log: color = curses.color_pair(4)
            elif "[-]" in log: color = curses.color_pair(7) | curses.A_BOLD
            elif "->" in log: color = curses.color_pair(3)
            
            safe_log = log[:max_x-4]
            stdscr.addstr(start_y + 2 + i, 2, safe_log, color)
            
        stdscr.refresh()
        time.sleep(0.1)
        
    stdscr.addstr(max_y - 1, 2, " PROCESS COMPLETED! Press ANY KEY to exit. ", curses.color_pair(2) | curses.A_BOLD)
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    try:
        curses.wrapper(run_tui)
    except KeyboardInterrupt:
        print("\n Execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n An unexpected error occurred: {e}")