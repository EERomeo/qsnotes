#!/usr/bin/env python3
"""
QSNotes - Quick & Simple Notes TUI
https://github.com/EERomeo/qsnotes
"""

import json
import curses
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class Note:
    _next_id = 1
    
    def __init__(self, title: str = "", body: str = "", note_id: Optional[int] = None):
        if note_id is None:
            self.id = Note._next_id
            Note._next_id += 1
        else:
            self.id = note_id
            if note_id >= Note._next_id:
                Note._next_id = note_id + 1
        
        self.title = title
        self.body = body
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        note = cls(data["title"], data["body"], data["id"])
        note.created_at = data.get("created_at", note.created_at)
        note.updated_at = data.get("updated_at", note.updated_at)
        return note
    
    def update(self, title: str, body: str):
        self.title = title
        self.body = body
        self.updated_at = datetime.now().isoformat()
    
    @classmethod
    def reset_id_counter(cls, notes: List["Note"]):
        if notes:
            max_id = max(note.id for note in notes)
            cls._next_id = max_id + 1
        else:
            cls._next_id = 1


class NoteManager:
    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            script_dir = Path(__file__).parent.absolute()
            self.file_path = script_dir / "notes.json"
        else:
            self.file_path = Path(file_path)
        
        self.notes: List[Note] = []
        self.load_notes()
        Note.reset_id_counter(self.notes)
    
    def load_notes(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.notes = [Note.from_dict(note_data) for note_data in data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.notes = []
        else:
            self.notes = []
    
    def save_notes(self) -> None:
        data = [note.to_dict() for note in self.notes]
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_note(self, title: str, body: str) -> Note:
        note = Note(title, body)
        self.notes.append(note)
        self.save_notes()
        return note
    
    def update_note(self, note_id: int, title: str, body: str) -> bool:
        for note in self.notes:
            if note.id == note_id:
                note.update(title, body)
                self.save_notes()
                return True
        return False
    
    def delete_note(self, note_id: int) -> bool:
        self.notes = [note for note in self.notes if note.id != note_id]
        self.save_notes()
        return True
    
    def get_note(self, note_id: int) -> Optional[Note]:
        for note in self.notes:
            if note.id == note_id:
                return note
        return None
    
    def search_notes(self, search_term: str) -> List[Note]:
        if not search_term:
            return self.notes
        
        results = []
        search_lower = search_term.lower()
        
        for note in self.notes:
            if (search_lower in note.title.lower() or 
                search_lower in note.body.lower()):
                results.append(note)
        
        return results

class QSNotes:
    """Terminal TUI using curses"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.note_manager = NoteManager()
        self.current_note_id: Optional[int] = None
        self.search_term = ""
        self.selected_index = 0
        self.last_selected_index = 0  # track last selection
        self.mode = "list"  # "list", "edit", "new"
        self.editing_title = ""
        self.editing_body = ""
        self.show_search = False
        self.notes_per_page = 0
        self.current_field = "title"  # "title" or "body"
        self.cursor_pos = 0  # Cursor position in current field
        self.body_cursor_row = 0  # Current row in body (for multiline)
        self.body_cursor_col = 0  # Current column in body
        self._last_height = 0
        self._last_width = 0
        self.body_scroll = 0
        self.preview_scroll = 0
        self.LIST_VISIBLE_COUNT = 5
        
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(0)  # Blocking input
        self.stdscr.keypad(True)  # Enable special keys
        
        # Define color pairs (terminal colors)
        curses.start_color()
        curses.use_default_colors()  # Use terminal default colors
        
        # Create color pairs
        curses.init_pair(1, curses.COLOR_BLUE, -1)      #
        curses.init_pair(2, curses.COLOR_WHITE, -1)     #  
        curses.init_pair(3, curses.COLOR_CYAN, -1)      #
        curses.init_pair(4, -1, curses.COLOR_BLUE)      #
        curses.init_pair(5, curses.COLOR_GREEN, -1)     #
        curses.init_pair(6, curses.COLOR_RED, -1)       #
        curses.init_pair(7, curses.COLOR_YELLOW, -1)    #
        curses.init_pair(8, curses.COLOR_MAGENTA, -1)   #
    
    def draw_box(self, y: int, x: int, height: int, width: int, title: str = "", color_pair: int = 0) -> None:
        # Top border
        self.stdscr.attron(curses.color_pair(color_pair))
        self.stdscr.addch(y, x, curses.ACS_ULCORNER)
        self.stdscr.hline(y, x + 1, curses.ACS_HLINE, width - 2)
        self.stdscr.addch(y, x + width - 1, curses.ACS_URCORNER)
        
        # Title if provided
        if title:
            title_x = x + 2
            if color_pair:
                self.stdscr.attron(curses.color_pair(color_pair))
            self.stdscr.addstr(y, title_x, title)
            if color_pair:
                self.stdscr.attroff(curses.color_pair(color_pair))
        
        # Sides
        self.stdscr.attron(curses.color_pair(color_pair))
        for row in range(y + 1, y + height - 1):
            self.stdscr.addch(row, x, curses.ACS_VLINE)
            self.stdscr.addch(row, x + width - 1, curses.ACS_VLINE)
        
        # Bottom border
        self.stdscr.addch(y + height - 1, x, curses.ACS_LLCORNER)
        self.stdscr.hline(y + height - 1, x + 1, curses.ACS_HLINE, width - 2)
        self.stdscr.addch(y + height - 1, x + width - 1, curses.ACS_LRCORNER)
    
    def draw_list_view(self) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        
        # Main box
        self.draw_box(1, 2, height - 5, width - 4, " QSNotes ", 3)
        
        # Command hints box at bottom
        self.draw_box(height - 4, 2, 4, width - 4, "", 5)
        hints = "n:New  Enter:Edit  d:Delete  /:Search  q:Quit"
        hints_x = (width - len(hints)) // 2
        self.stdscr.addstr(height - 3, hints_x, hints, curses.color_pair(3))
        
        # Search bar if active
        if self.show_search:
            search_text = f"Search: {self.search_term}"
            self.stdscr.addstr(3, 4, "Search: ", curses.color_pair(1))
            self.stdscr.addstr(3, 12, self.search_term, curses.color_pair(2))
            curses.curs_set(1)  # Show cursor for input
            self.stdscr.move(3, 12 + len(self.search_term))
        else:
            curses.curs_set(0)  # Hide cursor
        
        # Notes list
        notes = self.note_manager.search_notes(self.search_term)
        sorted_notes = sorted(notes, key=lambda x: x.id)
        
        # Calculate display
        self.notes_per_page = self.LIST_VISIBLE_COUNT
        start_index = 0
        if len(sorted_notes) > self.notes_per_page:
            if self.selected_index >= self.notes_per_page:
                start_index = self.selected_index - self.notes_per_page + 1
        
        # Header
        header = "Title                            Created      Updated"
        self.stdscr.addstr(4, 4, header, curses.color_pair(1))
        self.stdscr.hline(5, 4, curses.ACS_HLINE, width - 8)
        
        # Notes
        for i, note in enumerate(sorted_notes[start_index:start_index + self.notes_per_page]):
            y = 6 + i
            is_selected = (i + start_index) == self.selected_index
            
            # Format data
            title = (note.title[:27] + "...") if len(note.title) > 27 else note.title.ljust(30)
            title = title or "(Untitled)"
            created = datetime.fromisoformat(note.created_at).strftime("%Y-%m-%d")
            updated = datetime.fromisoformat(note.updated_at).strftime("%Y-%m-%d")
            
            # Draw
            line = f"{title:30}  {created:10}  {updated:10}"
            if is_selected:
                self.stdscr.addstr(y, 4, line, curses.color_pair(4))
            else:
                self.stdscr.addstr(y, 4, line, curses.color_pair(2))

            preview_separator_y = 6 + self.LIST_VISIBLE_COUNT
            self.stdscr.hline(preview_separator_y, 4, curses.ACS_HLINE, width - 8)

            selected_note = None
            if 0 <= self.selected_index < len(sorted_notes):
                selected_note = sorted_notes[self.selected_index]
            preview_lines = []
            max_width = width - 8

            if selected_note:
                for line in selected_note.body.split("\n"):
                    if line == "":
                        preview_lines.append("")
                    else:
                        for i in range(0, len(line), max_width):
                            preview_lines.append(line[i:i + max_width])
            preview_top = preview_separator_y + 1
            preview_bottom = height - 6
            preview_height = preview_bottom - preview_top

            max_scroll = max(0, len(preview_lines) - preview_height)
            self.preview_scroll = max(0, min(self.preview_scroll, max_scroll))
            for i in range(preview_height):
                idx = self.preview_scroll + i
                if idx >= len(preview_lines):
                    break
                self.stdscr.addstr(
                    preview_top + i,
                    4,
                    preview_lines[idx],
                    curses.color_pair(3)
                )

        # No notes message
        if not sorted_notes:
            msg = "No notes yet. Press 'n' to create one!"
            if self.search_term:
                msg = f"No notes found for '{self.search_term}'"
            msg_x = (width - len(msg)) // 2
            self.stdscr.addstr(6, msg_x, msg, curses.color_pair(3))
        
        self.stdscr.noutrefresh()
        curses.doupdate()
    
    def draw_edit_view(self) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()

        # Layout constants
        body_top = 7
        body_bottom = height - 6
        max_body_lines = body_bottom - body_top
        max_line_width = width - 8

        # Main boxes
        self.draw_box(1, 2, height - 5, width - 4, " QNotes ", 3)
        self.draw_box(height - 4, 2, 4, width - 4, "", 5)

        hints = "Tab:Switch  Alt+S/Ctrl+W:Save  Esc:Cancel/Exit"
        self.stdscr.addstr(height - 3, (width - len(hints)) // 2, hints, curses.color_pair(3))

        # ----- TITLE -----
        self.stdscr.addstr(3, 4, "Title:", curses.color_pair(1))

        display_title = self.editing_title
        if len(display_title) > max_line_width:
            display_title = display_title[: max_line_width - 3] + "..."

        self.stdscr.addstr(4, 4, display_title, curses.color_pair(2))

        # ----- BODY -----
        self.stdscr.addstr(6, 4, "Content:", curses.color_pair(1))
        body_lines = self.editing_body.split("\n") or [""]

        # Build wrapped line map: [(orig_row, start_col)]
        self.wrapped_line_map = []

        for row_idx, line in enumerate(body_lines):
            if line == "":
                self.wrapped_line_map.append((row_idx, 0))
            else:
                for start in range(0, len(line), max_line_width):
                    self.wrapped_line_map.append((row_idx, start))

        if not self.wrapped_line_map:
            self.wrapped_line_map.append((0, 0))

        # Clamp scroll
        max_scroll = max(0, len(self.wrapped_line_map) - max_body_lines)
        self.body_scroll = max(0, min(self.body_scroll, max_scroll))

        # Draw visible body slice
        visible = self.wrapped_line_map[
            self.body_scroll : self.body_scroll + max_body_lines
        ]

        for i, (row, col) in enumerate(visible):
            line = body_lines[row][col : col + max_line_width]
            self.stdscr.addstr(body_top + i, 4, line, curses.color_pair(2))

        # ----- ACTIVE FIELD INDICATOR -----
        if self.current_field == "title":
            self.stdscr.addch(3, 3, ">", curses.color_pair(1))
        else:
            self.stdscr.addch(6, 3, ">", curses.color_pair(1))

        # ----- CURSOR POSITION -----
        if self.current_field == "title":
            cursor_y = 4
            cursor_x = 4 + min(self.cursor_pos, max_line_width)
        else:
            # Find wrapped line index of cursor
            wrapped_idx = 0
            for i, (r, c) in enumerate(self.wrapped_line_map):
                if r == self.body_cursor_row and self.body_cursor_col >= c:
                    wrapped_idx = i

            # Auto-scroll to keep cursor visible
            if wrapped_idx < self.body_scroll:
                self.body_scroll = wrapped_idx
            elif wrapped_idx >= self.body_scroll + max_body_lines:
                self.body_scroll = wrapped_idx - max_body_lines + 1

            # Re-clamp
            self.body_scroll = max(0, min(self.body_scroll, max_scroll))

            screen_row = wrapped_idx - self.body_scroll
            start_col = self.wrapped_line_map[wrapped_idx][1]

            cursor_y = body_top + screen_row
            cursor_x = 4 + min(
                self.body_cursor_col - start_col, max_line_width - 1
            )

        curses.curs_set(1)
        self.stdscr.move(cursor_y, min(cursor_x, width - 5))
        self.stdscr.noutrefresh()
        curses.doupdate()

    
    def check_save_key(self, key: int) -> bool:
        """Check if key is a save key combination. Returns True if save should occur."""
        # Try multiple save key combinations
        save_keys = [
            23,    # Ctrl+W (ASCII 23)
            15,    # Ctrl+O (ASCII 15)
        ]
        
        return key in save_keys
    
    def handle_list_mode(self, key: int) -> bool:
        if self.show_search:
            if key in (curses.KEY_BACKSPACE, 127):
                self.search_term = self.search_term[:-1]
                self.draw_list_view()
            elif key == 27:  # Esc
                self.show_search = False
                self.search_term = ""
                self.draw_list_view()
            elif key == 10:  # Enter
                notes = self.note_manager.search_notes(self.search_term)
                sorted_notes = sorted(notes, key=lambda x: x.id)
                if 0 <= self.selected_index < len(sorted_notes):
                    note = sorted_notes[self.selected_index]
                    self.mode = "edit"
                    self.current_note_id = note.id
                    self.editing_title = note.title
                    self.editing_body = note.body

                    # Jump straight into body
                    self.current_field = "body"
                    body_lines = self.editing_body.split("\n") or [""]
                    self.body_cursor_row = len(body_lines) - 1
                    self.body_cursor_col = len(body_lines[-1])

                    # Title cursor is still valid if user tabs back
                    self.cursor_pos = len(self.editing_title)

                    # Reset body scroll so draw_edit_view can reposition it
                    self.body_scroll = 0
                    self.last_selected_index = self.selected_index  # SAVE SELECTION
                    self.draw_edit_view()
            elif 32 <= key <= 126:
                self.search_term += chr(key)
                self.draw_list_view()
            return True
        #Handle keys in list mode. Returns True if should continue, False if quit.
        if key == ord('q'):
            return False
        elif key == ord('n'):
            self.mode = "new"
            self.current_note_id = None
            self.editing_title = ""
            self.editing_body = ""
            self.current_field = "title"
            self.cursor_pos = 0
            self.body_cursor_row = 0
            self.body_cursor_col = 0
            self.draw_edit_view()
        elif key == ord('/'):
            self.show_search = not self.show_search
            if not self.show_search:
                self.search_term = ""
            self.draw_list_view()
        elif key == 10:  # Enter
            notes = self.note_manager.search_notes(self.search_term)
            sorted_notes = sorted(notes, key=lambda x: x.id)
            if 0 <= self.selected_index < len(sorted_notes):
                note = sorted_notes[self.selected_index]
                self.mode = "edit"
                self.current_note_id = note.id
                self.editing_title = note.title
                self.editing_body = note.body

                # Jump straight into body
                self.current_field = "body"
                body_lines = self.editing_body.split("\n") or [""]
                self.body_cursor_row = len(body_lines) - 1
                self.body_cursor_col = len(body_lines[-1])

                # Title cursor is still valid if user tabs back
                self.cursor_pos = len(self.editing_title)

                # Reset body scroll so draw_edit_view can reposition it
                self.body_scroll = 0
                self.last_selected_index = self.selected_index  # SAVE SELECTION
                self.draw_edit_view()
        elif key == ord('d'):
            notes = self.note_manager.search_notes(self.search_term)
            sorted_notes = sorted(notes, key=lambda x: x.id)
            if 0 <= self.selected_index < len(sorted_notes):
                note = sorted_notes[self.selected_index]
                self.note_manager.delete_note(note.id)
                if self.selected_index >= len(sorted_notes) - 1:
                    self.selected_index = max(0, len(sorted_notes) - 2)
                self.draw_list_view()
                self.preview_scroll = 0

        elif key == curses.KEY_UP:
            notes = self.note_manager.search_notes(self.search_term)
            if notes:
                self.selected_index = (self.selected_index - 1) % len(notes)
                self.draw_list_view()
                self.preview_scroll = 0

        elif key == curses.KEY_DOWN:
            notes = self.note_manager.search_notes(self.search_term)
            if notes:
                self.selected_index = (self.selected_index + 1) % len(notes)
                self.draw_list_view()
                self.preview_scroll = 0

        elif self.show_search:
            if key == curses.KEY_BACKSPACE or key == 127:
                self.search_term = self.search_term[:-1]
                self.draw_list_view()
            elif key == 27:  # Escape
                self.show_search = False
                self.search_term = ""
                self.draw_list_view()
            elif 32 <= key <= 126:  # Printable ASCII
                self.search_term += chr(key)
                self.draw_list_view()
            self.preview_scroll = 0

        return True
    
    def handle_edit_mode(self, key: int):
        # First check for control keys
        if key == 27:  # Escape - Cancel
            self.mode = "list"
            # DON'T reset selected_index = 0, keep the last selection
            self.draw_list_view()
            return
        
        # Check for save keys
        if self.check_save_key(key):
            if self.editing_title.strip() or self.editing_body.strip():
                if self.current_note_id:
                    # Update existing note - keep selection
                    self.note_manager.update_note(
                        self.current_note_id, 
                        self.editing_title, 
                        self.editing_body
                    )
                    # Keep the same selected_index (it points to the updated note)
                else:
                    # Create new note - select the new note
                    new_note = self.note_manager.add_note(
                        self.editing_title, 
                        self.editing_body
                    )
                    # Find the index of the new note
                    notes = self.note_manager.search_notes(self.search_term)
                    sorted_notes = sorted(notes, key=lambda x: x.id)
                    for i, note in enumerate(sorted_notes):
                        if note.id == new_note.id:
                            self.selected_index = i
                            break
            self.mode = "list"
            self.draw_list_view()
            return

        if key == 9:  # Tab - switch between title and body
            if self.current_field == "title":
                self.current_field = "body"
                # Initialize cursor position in body
                body_lines = self.editing_body.split('\n')
                if body_lines:
                    self.body_cursor_row = len(body_lines)
                    self.body_cursor_col = min(self.cursor_pos, len(body_lines[0]))
                else:
                    self.body_cursor_col = 0
            else:
                self.current_field = "title"
                # Set cursor position based on where we were in body
                self.cursor_pos = self.body_cursor_col
            self.draw_edit_view()
            return
        
        # Now handle text editing based on current field
        if self.current_field == "title":
            self.handle_title_input(key)
        else:
            self.handle_body_input(key)
    
    def handle_title_input(self, key: int):
        if key == curses.KEY_BACKSPACE or key == 127:
            if self.cursor_pos > 0:
                self.editing_title = self.editing_title[:self.cursor_pos-1] + self.editing_title[self.cursor_pos:]
                self.cursor_pos -= 1
            self.draw_edit_view()
        elif key == curses.KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
            self.draw_edit_view()
        elif key == curses.KEY_RIGHT:
            if self.cursor_pos < len(self.editing_title):
                self.cursor_pos += 1
            self.draw_edit_view()
        elif 32 <= key <= 126:
            self.editing_title = self.editing_title[:self.cursor_pos] + chr(key) + self.editing_title[self.cursor_pos:]
            self.cursor_pos += 1
            self.draw_edit_view()
    
    def handle_body_input(self, key: int):
        body_lines = self.editing_body.split('\n')
        # Ensure we have at least one line
        if not body_lines:
            body_lines = [""]
        
        # Make sure body_cursor_row is within bounds
        if self.body_cursor_row >= len(body_lines):
            self.body_cursor_row = max(0, len(body_lines) - 1)
        
        # Ensure body_cursor_row is not negative
        if self.body_cursor_row < 0:
            self.body_cursor_row = 0
        
        # Get current line
        if self.body_cursor_row < len(body_lines):
            current_line = body_lines[self.body_cursor_row]
        else:
            current_line = ""
        
        # Ensure body_cursor_col is within bounds
        if self.body_cursor_col > len(current_line):
            self.body_cursor_col = len(current_line)
        if self.body_cursor_col < 0:
            self.body_cursor_col = 0
        
        # Handle backspace (delete left)
        if key == curses.KEY_BACKSPACE or key == 127:
            if self.body_cursor_col > 0:
                # Delete character before cursor
                new_line = current_line[:self.body_cursor_col-1] + current_line[self.body_cursor_col:]
                body_lines[self.body_cursor_row] = new_line
                self.editing_body = '\n'.join(body_lines)
                self.body_cursor_col -= 1
            elif self.body_cursor_row > 0:
                # Join with previous line
                prev_line = body_lines[self.body_cursor_row-1]
                body_lines[self.body_cursor_row-1] = prev_line + current_line
                del body_lines[self.body_cursor_row]
                self.editing_body = '\n'.join(body_lines)
                self.body_cursor_row -= 1
                self.body_cursor_col = len(prev_line)
            self.draw_edit_view()
        
        # Handle delete (delete right)
        elif key == curses.KEY_DC:
            if self.body_cursor_col < len(current_line):
                # Delete character at cursor
                new_line = current_line[:self.body_cursor_col] + current_line[self.body_cursor_col+1:]
                body_lines[self.body_cursor_row] = new_line
                self.editing_body = '\n'.join(body_lines)
            elif self.body_cursor_row < len(body_lines) - 1:
                # Join with next line
                next_line = body_lines[self.body_cursor_row+1]
                body_lines[self.body_cursor_row] = current_line + next_line
                del body_lines[self.body_cursor_row+1]
                self.editing_body = '\n'.join(body_lines)
            self.draw_edit_view()
        
        elif key == 10:  # Enter - new line
            # Split current line at cursor
            left_part = current_line[:self.body_cursor_col]
            right_part = current_line[self.body_cursor_col:]
            
            body_lines[self.body_cursor_row] = left_part
            body_lines.insert(self.body_cursor_row + 1, right_part)
            self.editing_body = '\n'.join(body_lines)
            self.body_cursor_row += 1
            self.body_cursor_col = 0
            self.draw_edit_view()
        
        elif key == curses.KEY_LEFT:
            if self.body_cursor_col > 0:
                self.body_cursor_col -= 1
            elif self.body_cursor_row > 0:
                self.body_cursor_row -= 1
                # Get the new current line
                if self.body_cursor_row < len(body_lines):
                    self.body_cursor_col = len(body_lines[self.body_cursor_row])
                else:
                    self.body_cursor_col = 0
            self.draw_edit_view()
        
        elif key == curses.KEY_RIGHT:
            if self.body_cursor_col < len(current_line):
                self.body_cursor_col += 1
            elif self.body_cursor_row < len(body_lines) - 1:
                self.body_cursor_row += 1
                self.body_cursor_col = 0
            self.draw_edit_view()
        
        elif key == curses.KEY_UP:
            if self.body_cursor_row > 0:
                self.body_cursor_row -= 1
                # Get the new current line
                if self.body_cursor_row < len(body_lines):
                    # Keep cursor column within bounds of new line
                    new_line_len = len(body_lines[self.body_cursor_row])
                    self.body_cursor_col = min(self.body_cursor_col, new_line_len)
                else:
                    self.body_cursor_col = 0
            self.draw_edit_view()
        
        elif key == curses.KEY_DOWN:
            if self.body_cursor_row < len(body_lines) - 1:
                self.body_cursor_row += 1
                # Get the new current line
                if self.body_cursor_row < len(body_lines):
                    # Keep cursor column within bounds of new line
                    new_line_len = len(body_lines[self.body_cursor_row])
                    self.body_cursor_col = min(self.body_cursor_col, new_line_len)
                else:
                    self.body_cursor_col = 0
            self.draw_edit_view()
        
        elif key == curses.KEY_HOME:
            self.body_cursor_col = 0
            self.draw_edit_view()
        
        elif key == curses.KEY_END:
            if self.body_cursor_row < len(body_lines):
                self.body_cursor_col = len(body_lines[self.body_cursor_row])
            self.draw_edit_view()
        
        elif 32 <= key <= 126:
            # Insert character at cursor position
            new_line = current_line[:self.body_cursor_col] + chr(key) + current_line[self.body_cursor_col:]
            body_lines[self.body_cursor_row] = new_line
            self.editing_body = '\n'.join(body_lines)
            self.body_cursor_col += 1
            self.draw_edit_view()
    
    def run(self) -> None:
        self.draw_list_view()
        last_key = None
        
        while True:
            try:
                key = self.stdscr.getch()
                last_key = key
                
                if self.mode == "list":
                    if not self.handle_list_mode(key):
                        break  # Quit if handle_list_mode returns False
                elif self.mode in ["edit", "new"]:
                    self.handle_edit_mode(key)
                        
            except KeyboardInterrupt:
                break


def main(stdscr):
    """Main entry point for curses"""
    app = QSNotes(stdscr)
    app.run()


if __name__ == "__main__":
    # Run the curses application
    curses.wrapper(main)
