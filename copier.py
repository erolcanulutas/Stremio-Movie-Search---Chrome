import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

FILE_EXTENSIONS = ('.py', '.json', '.ino', '.js', '.html')
BASE_DIR = os.getcwd()
CURRENT_SCRIPT = os.path.basename(sys.argv[0])

# ----------------------------
# Helpers
# ----------------------------
def is_valid_file(path: str) -> bool:
    return (
        os.path.isfile(path)
        and path.endswith(FILE_EXTENSIONS)
        and os.path.basename(path) != CURRENT_SCRIPT
    )

def rel_display(path: str) -> str:
    return os.path.relpath(path, BASE_DIR).replace("\\", "/")

# ----------------------------
# Checkbox state (PATH-based)
# ----------------------------
checked_paths = set()     # full_path set
tree_items = {}           # item_id -> full_path

# ----------------------------
# Tree events
# ----------------------------
def toggle_item(event):
    element = tree.identify("element", event.x, event.y)
    if element not in ("text", "image"):
        return

    item = tree.identify_row(event.y)
    if not item or item not in tree_items:
        return

    path = tree_items[item]

    if path in checked_paths:
        checked_paths.remove(path)
        tree.item(item, text=tree.item(item, "text").replace("☑ ", "☐ ", 1))
    else:
        checked_paths.add(path)
        tree.item(item, text=tree.item(item, "text").replace("☐ ", "☑ ", 1))

    load_selected_files()

# ----------------------------
# Build tree (preserve checks)
# ----------------------------
def build_tree():
    tree.delete(*tree.get_children())
    tree_items.clear()

    root_node = tree.insert("", "end", text="📁 project", open=True)

    def add_folder(parent, folder_path):
        try:
            entries = sorted(os.listdir(folder_path))
        except PermissionError:
            return

        folders, files = [], []

        for entry in entries:
            full_path = os.path.join(folder_path, entry)
            if os.path.isdir(full_path):
                folders.append((entry, full_path))
            elif is_valid_file(full_path):
                files.append((entry, full_path))

        for name, full_path in folders:
            node = tree.insert(parent, "end", text=f"📁 {name}", open=False)
            add_folder(node, full_path)

        for name, full_path in files:
            prefix = "☑ " if full_path in checked_paths else "☐ "
            node = tree.insert(parent, "end", text=f"{prefix}{name}")
            tree_items[node] = full_path

    add_folder(root_node, BASE_DIR)

# ----------------------------
# Check / Uncheck ALL
# ----------------------------
def check_all():
    checked_paths.clear()
    for item, path in tree_items.items():
        checked_paths.add(path)
        tree.item(item, text=tree.item(item, "text").replace("☐ ", "☑ ", 1))
    load_selected_files()

def uncheck_all():
    checked_paths.clear()
    for item in tree_items:
        tree.item(item, text=tree.item(item, "text").replace("☑ ", "☐ ", 1))
    load_selected_files()

# ----------------------------
# Dump selected files
# ----------------------------
def load_selected_files():
    text_box.config(state="normal")
    text_box.delete("1.0", tk.END)

    for filepath in sorted(checked_paths):
        if not os.path.exists(filepath):
            continue

        text_box.insert(tk.END, f"{rel_display(filepath)}\n")
        text_box.insert(tk.END, "---\n")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"[Error reading file: {e}]"

        text_box.insert(tk.END, content + "\n")
        text_box.insert(tk.END, "---\n\n")

    text_box.config(state="disabled")

# ----------------------------
# Clipboard
# ----------------------------
def copy_all():
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", tk.END))
    root.update()

def refresh_and_copy():
    load_selected_files()
    copy_all()

# ----------------------------
# UI
# ----------------------------
root = tk.Tk()
root.title("Copier - Project File Dumper")

main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

# --- Left panel ---
left_frame = ttk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)

tree = ttk.Treeview(left_frame, show="tree", height=35)
tree.pack(fill="y", expand=True)
tree.bind("<Button-1>", toggle_item)

ttk.Button(left_frame, text="Refresh Tree", command=build_tree).pack(fill="x", pady=(8, 4))
ttk.Button(left_frame, text="Check All", command=check_all).pack(fill="x", pady=2)
ttk.Button(left_frame, text="Uncheck All", command=uncheck_all).pack(fill="x", pady=2)

# --- Right panel ---
right_frame = ttk.Frame(main_frame)
right_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

text_box = scrolledtext.ScrolledText(right_frame, wrap="word", width=110, height=40)
text_box.pack(fill="both", expand=True)

# --- Bottom buttons (centered + right) ---
button_frame = ttk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=(0, 10))

button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=0)
button_frame.columnconfigure(2, weight=1)

center_group = ttk.Frame(button_frame)
center_group.grid(row=0, column=1)

ttk.Button(center_group, text="Refresh Text", command=load_selected_files).pack(side="left", padx=5)
ttk.Button(center_group, text="Copy All", command=copy_all).pack(side="left", padx=5)

ttk.Button(
    button_frame,
    text="Refresh & Copy All",
    command=refresh_and_copy
).grid(row=0, column=2, sticky="e")

# ----------------------------
# Init
# ----------------------------
build_tree()
root.mainloop()
