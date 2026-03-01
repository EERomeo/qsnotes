# QSNotes (Quick & Simple Notes TUI)

A fast, terminal‑native note‑taking application written in Python using `curses`.

QSNotes is designed to feel like a minimal and light TUI: terminal colors, keyboard‑only workflow, instant preview.

<img width="600" height="600" alt="image" src="https://github.com/user-attachments/assets/2dbd0fc9-9b17-420c-bca3-9dceadafa3ca" />
<img width="600" height="600" alt="image" src="https://github.com/user-attachments/assets/3c06bc17-ee6f-4a97-b4a4-0f900548f6f3" />

---
## 🚀 What's New in v1.1.0
### 📝 Streamlined Note Taking
No more title field - The title is now automatically taken from the first line of your note

Faster editing - Jump straight into writing without switching between fields

One-line notes - Perfect for quick thoughts, the title becomes the content itself

### ⌨️ Scrollable Preview
Browse note contents directly in the list view even if the body is bigger than the viewport

Use j/k keys to scroll through the body of the selected note

See all of your notes without opening them

### 🚀 Command Line Superpowers
Quick notes from terminal:
```bash
# Create a note and exit immediately
./notes.py --quick "Buy milk and eggs"
# or with the short option
./notes.py -q "Meeting at 3pm"
```

Start directly in edit mode:
```bash
# Open ready to write a new note
./notes.py --new
# or with the short option
./notes.py -n
```

Pre-filled templates:
```bash
# Start a new note with text already entered
./notes.py --new --body "TODO: "
./notes.py -n -b "Meeting notes:"
```

Pipe content directly:
```bash
# Create notes from other commands
echo "Quick thought" | ./notes.py --pipe
cat meeting_notes.txt | ./notes.py --pipe
curl -s https://example.com/note.txt | ./notes.py --pipe
```

### 🔧 Bash/Zsh Integration
Add this to your .bashrc or .zshrc for the ultimate quick-note experience:
```bash
# Quick note function
qn() {
    local NOTES_SCRIPT="/path/to/your/notes.py"
    
    if [ ! -t 0 ]; then
        # Input from pipe
        cat - | "$NOTES_SCRIPT" --pipe && echo "QN OK"
    elif [ $# -eq 0 ]; then
        # No arguments - open in new note mode
        "$NOTES_SCRIPT" --new
    else
        # With arguments - create quick note
        "$NOTES_SCRIPT" --quick "$*" && echo "QN OK"
    fi
}
```

Then use it from anywhere:
```bash
$ qn                                # Opens editor for a new note
$ qn Buy milk                       # Creates quick note without opening the TUI
$ echo "Remember to call mom" | qn  # Creates note from piped input
$ cat todo.txt | qn                 # Import entire file as a note
```

### ✨ Clean Exits
No more error messages when quitting

q and Ctrl+O both exit cleanly

### 🔄 Fully Backward Compatible
Your existing notes work exactly as before

Same notes.json format

---
## ✨ Features

- 📝 Create, view, edit, delete notes
- 🔍 Fuzzy search in title and body
- 📋 Compact list view with **live note preview**
- ✏️ Note editor
- 💾 Persistent storage (`notes.json`)
- 🖥️ True terminal UI — no mouse needed

---

## 📦 Requirements

- Python **3.9+** (recommended)
- A Unix‑like terminal (Linux, macOS)
- Terminal must support `curses`
- Python libraries required: json, curses, datetime, pathlib, typing, argparse.

---

## 🚀 Installation

Clone the repository:

```sh
git clone https://github.com/EERomeo/qsnotes.git
cd qsnotes
```
Or download the latest release.

To better manage your system, it would be wise to have a dedicated 'scripts' directory. In that case, copy the cloned 'qsnotes' directory to your scripts directory and cd into it.

Make the script executable:

```sh
chmod +x qsnotes.py
```

---

## ▶️ Usage

Run directly:

```sh
python3 qsnotes.py
```

Or:

```sh
./qsnotes.py
```

Notes are stored locally in `notes.json` (created automatically).

---

## ⌨️ Keybindings

### Global (List View)

| Key | Action |
|---|---|
| `↑` / `↓` | Move selection |
| `Enter` | Edit selected note |
| `n` | New note |
| `d` | Delete selected note |
| `/` | Search notes |
| `q` | Quit |
| `j/k` | Scroll body |

### Search Mode

| Key | Action |
|---|---|
| Type text | Filter notes |
| `Backspace` | Delete character |
| `Enter` | Open seleted note |
| `Esc` | Exit search |

### Edit Mode

| Key | Action |
|---|---|
| `Ctrl+W` | Save |
| `Ctrl+O` | Save & Exit |
| `Esc` | Cancel and return to list |
| `Arrows` | Move cursor |

---

## 🧭 List + Preview Layout

QSNotes shows:

- A **compact list** of notes (fixed size)
- A **read‑only preview** of the selected note body

This allows quick browsing without entering edit mode.

---

## 🪟 Hyprland / Wayland (Optional)

QSNotes runs inside your terminal. It is better if it opens in a small floating window.

Example keybind on Omarchy (add to ~/.config/hypr/bindings.conf):

```ini
bindd = SUPER, N, QSNotes, exec, omarchy-launch-tui python3 <path to>/qsnotes.py
bindd = SUPER SHIFT, N, QSNotes new, exec, omarchy-launch-tui python3 <path to>/qsnotes.py -n
```

Hyprland window rules (add to ~/.config/hypr/hyprland.conf):

```ini
windowrule = match:class org.omarchy.python3, float on
windowrule = match:class org.omarchy.python3, size 600 600
```

---

## 📁 Project Structure

```text
qsnotes.py      # Main application
notes.json     # Notes storage (auto‑generated)
README.md
```

---

## 🔧 Customizing

You can change some of the behaviour to better suit your workflow.
Here are some hints:
- On line 202 you can change the sorting behaviour as well as what the sorting works on. Changing x.id to x.created_at or x.updated_at will sort on the creation or last updated date. Change reverse=True to reverse=False to sort ascending or descending. Default sort is on note id.

---

## 🧠 Design Goals

- Minimal dependencies
- Easy to use
- Out of your way
- Easy to extend and hack on

This project is meant to be *readable* and *modifiable*.

---

## 📜 License

MIT License

Feel free to use, modify, share, discombobulate or whatever you feel like.

---

## ❤️ Acknowledgements

Inspired by DHH's Omarchy minimalistic but functional approach.

Happy note‑taking!
