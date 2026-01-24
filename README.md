# QSNotes (Quick & Simple Notesm TUI)

A fast, terminal‑native note‑taking application written in Python using `curses`.

QSNotes is designed to feel like a minimal and light TUI: terminal colors, keyboard‑only workflow, instant preview.

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
- Python libraries required: json, curses, datetime, pathlib, typing.

---

## 🚀 Installation

Clone the repository:

```sh
git clone https://github.com/EERomeo/qsnotes.git
cd qsnotes
```

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
| `Tab` | Switch between title and body |
| `Ctrl+W` | Save |
| `Esc` | Cancel and return to list |
| Arrow keys | Move cursor |

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
bindd = SUPER SHIFT, N QSNotes, exec, omarchy-launch-tui python3 <path to>/qsnotes.py
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
