#!/usr/bin/env python3

import os
import sys
import curses

# شعار HashReveal الجديد
LOGO = [
    " ██╗  ██╗ █████╗ ███████╗██╗  ██╗██████╗ ███████╗██╗   ██╗███████╗█████╗ ██╗     ",
    " ██║  ██║██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██║     ",
    " ███████║███████║███████╗███████║██████╔╝█████╗  ██║   ██║█████╗  ███████║██║     ",
    " ██╔══██║██╔══██║╚════██║██╔══██║██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██║██║     ",
    " ██║  ██║██║  ██║███████║██║  ██║██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║███████╗",
    " ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝"
]

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
        # لتفادي الأخطاء إذا كانت الشاشة أصغر من الشعار
        x = max(0, (max_x - len(line)) // 2)
        try:
            stdscr.addstr(start_y + i, x, line[:max_x-1], curses.color_pair(8) | curses.A_BOLD)
        except curses.error:
            pass
    return start_y + len(LOGO) + 2

def prompt_input(stdscr, title, default_text=""):
    curses.curs_set(1)
    input_str = default_text
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, max_y // 4 - 2, max_x)
            box_w = min(80, max_x - 4)
            start_x = (max_x - box_w) // 2
            input_y = logo_bottom + 3
            
            stdscr.addstr(input_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(input_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            stdscr.addstr(input_y + 2, start_x, "│ ", curses.color_pair(5))
            stdscr.addstr(input_y + 2, start_x + 2, input_str.ljust(box_w-4), curses.color_pair(1))
            stdscr.addstr(input_y + 2, start_x + box_w - 2, " │", curses.color_pair(5))
            stdscr.addstr(input_y + 3, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            stdscr.move(input_y + 2, start_x + 2 + len(input_str))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c in (curses.KEY_ENTER, 10, 13): break
        elif c in (curses.KEY_BACKSPACE, 8, 127) and len(input_str) > 0: input_str = input_str[:-1]
        elif 32 <= c <= 126 and len(input_str) < box_w - 6: input_str += chr(c)
    curses.curs_set(0)
    return input_str.strip()

# New Multi-Select Function
def prompt_multiselect_scrollable(stdscr, options, title):
    current_idx = 0
    scroll_offset = 0
    selected = [False] * len(options)
    
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, 2, max_x)
            box_w = min(90, max_x - 4)
            start_x = (max_x - box_w) // 2
            start_y = logo_bottom + 2
            
            max_display = min(len(options), max_y - start_y - 6)
            if max_display < 1: max_display = 1
            
            if current_idx < scroll_offset: scroll_offset = current_idx
            elif current_idx >= scroll_offset + max_display: scroll_offset = current_idx - max_display + 1
            
            stdscr.addstr(start_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            
            for i in range(max_display):
                opt_idx = i + scroll_offset
                opt = options[opt_idx]
                y_pos = start_y + 2 + i
                
                prefix = "[*]" if selected[opt_idx] else "[ ]"
                color_text = curses.color_pair(2) if selected[opt_idx] else curses.color_pair(1)
                if opt_idx == current_idx:
                    color_text = curses.color_pair(7) | curses.A_BOLD
                
                label = f"  {prefix}  {opt.get('label', opt)} "
                if len(label) > box_w - 4: label = label[:box_w-7] + "..."
                label_padded = label.ljust(box_w - 4)
                
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                stdscr.addstr(y_pos, start_x + 2, label_padded, color_text)
                stdscr.addstr(y_pos, start_x + box_w - 2, " │", curses.color_pair(5))
                
            stdscr.addstr(start_y + 2 + max_display, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            
            controls = " [UP/DOWN] Navigate | [SPACE] Toggle | [A] Select All | [ENTER] Confirm "
            stdscr.addstr(start_y + 4 + max_display, (max_x - len(controls)) // 2, controls, curses.color_pair(5))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0: current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(options) - 1: current_idx += 1
        elif c == ord(' '): selected[current_idx] = not selected[current_idx]
        elif c in (ord('a'), ord('A')): 
            all_sel = all(selected)
            selected = [not all_sel] * len(options)
        elif c in (curses.KEY_ENTER, 10, 13): 
            return [options[i] for i in range(len(options)) if selected[i]]

def prompt_choice_scrollable(stdscr, options, title):
    current_idx = 0
    scroll_offset = 0
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, 2, max_x)
            box_w = min(90, max_x - 4)
            start_x = (max_x - box_w) // 2
            start_y = logo_bottom + 2
            
            max_display = min(len(options), max_y - start_y - 4)
            
            if current_idx < scroll_offset: scroll_offset = current_idx
            elif current_idx >= scroll_offset + max_display: scroll_offset = current_idx - max_display + 1
            
            stdscr.addstr(start_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            
            for i in range(max_display):
                opt_idx = i + scroll_offset
                opt = options[opt_idx]
                y_pos = start_y + 2 + i
                
                label = f"  {opt.get('icon', '•')}  {opt['label']} "
                if len(label) > box_w - 4: label = label[:box_w-7] + "..."
                label_padded = label.ljust(box_w - 4)
                
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                if opt_idx == current_idx:
                    stdscr.addstr(y_pos, start_x + 2, label_padded, curses.color_pair(7) | curses.A_BOLD)
                else:
                    stdscr.addstr(y_pos, start_x + 2, label_padded, curses.color_pair(1))
                stdscr.addstr(y_pos, start_x + box_w - 2, " │", curses.color_pair(5))
                
            stdscr.addstr(start_y + 2 + max_display, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0: current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(options) - 1: current_idx += 1
        elif c in (curses.KEY_ENTER, 10, 13): return current_idx

def crack_hash(stdscr, state):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    draw_logo(stdscr, 2, max_x)

    msg = " ⏳ Searching in pre-computed hash files... "
    stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg, curses.color_pair(3) | curses.A_BOLD)
    stdscr.refresh()

    wordlist_paths = state['wordlist_paths']
    target_hash = state['target_hash'].strip().lower()
    htype = state['hash_type']

    found = False
    plaintext = ""
    found_line_idx = -1
    source_file = ""

    for wordlist_path in wordlist_paths:
        base_name, ext = os.path.splitext(wordlist_path)
        hash_file_path = f"{base_name}_{htype}{ext}"

        if not os.path.exists(hash_file_path):
            continue # Skip files without pre-computed hashes

        try:
            with open(hash_file_path, "r", encoding="utf-8", errors="ignore") as h_file:
                for idx, line in enumerate(h_file):
                    if line.strip().lower() == target_hash:
                        found_line_idx = idx
                        source_file = os.path.basename(wordlist_path)
                        found = True
                        break
            
            if found:
                with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as w_file:
                    for idx, line in enumerate(w_file):
                        if idx == found_line_idx:
                            plaintext = line.strip()
                            break
                break # Exit the outer loop if found in any file
        except Exception:
            continue

    stdscr.clear()
    draw_logo(stdscr, 2, max_x)
    
    if found:
        res_msg = f" ✅ HASH FOUND! Plaintext: [{plaintext}] "
        color = curses.color_pair(2)
        line_msg = f" (Found in: {source_file} at line: {found_line_idx + 1}) "
        stdscr.addstr(max_y // 2 + 1, (max_x - len(line_msg)) // 2, line_msg, curses.color_pair(4))
    else:
        res_msg = " ❌ Hash not found in the selected wordlists. "
        color = curses.color_pair(7)

    stdscr.addstr(max_y // 2 - 1, (max_x - len(res_msg)) // 2, res_msg, color | curses.A_BOLD)
    stdscr.addstr(max_y // 2 + 3, (max_x - 25) // 2, " Press any key to return ", curses.color_pair(5))
    stdscr.refresh()
    stdscr.getch()

def run_dashboard(stdscr):
    state = {
        'hash_type': 'MD5',
        'wordlist_paths': [],
        'target_hash': 'None'
    }
    
    # تحديد مسار ملفات كلمات المرور
    base_dir = "Passwords/Common-Credentials"
    if not os.path.exists(base_dir):
        base_dir = "."
        
    current_idx = 0

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        display_names = f"{len(state['wordlist_paths'])} files selected" if state['wordlist_paths'] else "None"

        menu_items = [
            {"icon": "🔑", "key": "Hash Algorithm", "val": state['hash_type']},
            {"icon": "📁", "key": "Wordlist Files", "val": display_names},
            {"icon": "🎯", "key": "Target Hash", "val": state['target_hash']},
            {"icon": "🚀", "key": "START CRACKING", "val": ""}
        ]
        
        try:
            logo_bottom = draw_logo(stdscr, 2, max_x)
            box_w = min(85, max_x - 4)
            start_x = (max_x - box_w) // 2
            start_y = logo_bottom + 1
            
            stdscr.addstr(start_y, start_x, " 🛠️  HashReveal Dashboard ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            
            for i, item in enumerate(menu_items):
                y_pos = start_y + 2 + i
                left_text = f"  {item['icon']}  {item['key']}"
                
                display_val = item['val']
                if len(display_val) > 30:
                    display_val = display_val[:27] + "..."
                right_text = f"[{display_val}]  " if item['val'] else "  "
                
                pad_len = box_w - len(left_text) - len(right_text) - 2
                pad = " " * pad_len if pad_len > 0 else ""
                
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                
                if i == current_idx:
                    if item['key'] == "START CRACKING":
                        stdscr.addstr(y_pos, start_x + 2, (left_text + pad + right_text), curses.color_pair(10) | curses.A_BOLD)
                    else:
                        stdscr.addstr(y_pos, start_x + 2, (left_text + pad + right_text), curses.color_pair(6) | curses.A_BOLD)
                else:
                    if item['key'] == "START CRACKING":
                        stdscr.addstr(y_pos, start_x + 2, left_text, curses.color_pair(2) | curses.A_BOLD)
                    else:
                        stdscr.addstr(y_pos, start_x + 2, left_text, curses.color_pair(1))
                    stdscr.addstr(y_pos, start_x + 2 + len(left_text) + len(pad), right_text, curses.color_pair(3))
                    
                stdscr.addstr(y_pos, start_x + box_w - 2, " │", curses.color_pair(5))
                
            stdscr.addstr(start_y + 2 + len(menu_items), start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            stdscr.addstr(max_y - 2, 0, " Use UP/DOWN to navigate, ENTER to change, CTRL+C to quit. ".center(max_x), curses.color_pair(5))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0: current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(menu_items) - 1: current_idx += 1
        elif c in (curses.KEY_ENTER, 10, 13):
            if current_idx == 0:
                opts = [
                    {"icon": "⚡", "label": "MD5"},
                    {"icon": "⚡", "label": "SHA1"},
                    {"icon": "⚡", "label": "SHA224"},
                    {"icon": "⚡", "label": "SHA256"},
                    {"icon": "⚡", "label": "SHA384"},
                    {"icon": "⚡", "label": "SHA512"}
                ]
                choice = prompt_choice_scrollable(stdscr, opts, "🔑 Select Hash Type")
                state['hash_type'] = opts[choice]['label']

            elif current_idx == 1:
                try:
                    hash_suffixes = ["_MD5", "_SHA1", "_SHA224", "_SHA256", "_SHA384", "_SHA512"]
                    files = []
                    for f in os.listdir(base_dir):
                        if os.path.isfile(os.path.join(base_dir, f)):
                            base, ext = os.path.splitext(f)
                            if not any(base.endswith(suf) for suf in hash_suffixes):
                                files.append(f)
                    files.sort()
                    if not files: files = ["No files found"]
                except:
                    files = ["Error reading directory"]
                
                if files[0] not in ["No files found", "Error reading directory"]:
                    opts = [{"icon": "📄", "label": f} for f in files]
                    chosen = prompt_multiselect_scrollable(stdscr, opts, f"📁 Wordlists in {base_dir}")
                    if chosen:
                        state['wordlist_paths'] = [os.path.join(base_dir, c['label']) for c in chosen]
                else:
                    prompt_input(stdscr, f"⚠️ {files[0]}. Press Enter.")

            elif current_idx == 2:
                thash = prompt_input(stdscr, "🎯 Paste Target Hash Here")
                if thash:
                    state['target_hash'] = thash

            elif current_idx == 3:
                if not state['wordlist_paths'] or state['target_hash'] == 'None':
                    prompt_input(stdscr, "⚠️ Please select a wordlist and enter a hash first. Press Enter.")
                else:
                    crack_hash(stdscr, state)

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    run_dashboard(stdscr)

if __name__ == "__main__":
    try:
        curses.wrapper(main_tui)
    except KeyboardInterrupt:
        print("\n Execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n An unexpected error occurred: {e}")