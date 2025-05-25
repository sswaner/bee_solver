from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import Header, Footer, Static, Button, Input, ListView, ListItem
from textual.reactive import var
import string # For input validation
import random # For hint functionality

# Import solver functions
try:
    from solver import load_word_list, solve, pangram, score, length_histogram, length_table, add, remove
except ImportError:
    print("Error: Could not import from solver.py. Make sure it's in the same directory or PYTHONPATH.")
    pass


class SolverApp(App):
    """A Textual app for the Spelling Bee solver."""

    CSS_PATH = "tui_solver.css" 

    current_pattern = var("")
    main_word_list_data = var(list) # Renamed for clarity from main_word_list to avoid confusion with the widget
    extended_word_list_data = var(list) # Renamed for clarity
    
    # To store words for the hint provider
    _current_found_words = var(list)


    MAIN_WORDS_PATH = "wordlists/words.txt"
    EXTENDED_WORDS_PATH = "wordlists/xwi_bee_words.txt"
    ADDED_WORDS_PATH = "wordlists/added_words.txt"
    REMOVED_WORDS_PATH = "wordlists/removed_words.txt"


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="main_container"):
            yield Static("Welcome to Spelling Bee Solver!", id="status_display")
            
            with Horizontal(id="input_area"):
                yield Input(placeholder="Enter 7 puzzle letters", id="letters_input")
                yield Button("Solve", id="solve_button", variant="primary")
                yield Button("Hint", id="hint_button") # Added Hint button

            # Results Area - Middle Row, Column 1
            # Now contains two ListViews, so VerticalScroll might be better than Container
            with VerticalScroll(id="results_area"):
                yield Static("Found Words (Main):", classes="header")
                yield ListView(id="found_words_list")
                yield Static("Found Words (Extended/Bonus):", classes="header", id="extended_header") # Header for extended
                yield ListView(id="extended_words_list") # ListView for extended words

            # Stats Area - Middle Row, Column 2
            with VerticalScroll(id="stats_area"):
                yield Static("Statistics:", classes="header")
                yield Static("Score: 0", id="score_display")
                yield Static("Words (Main): 0", id="word_count_display")
                yield Static("Words (Extended): 0", id="extended_word_count_display") # For extended count
                yield Static("Pangrams: -", id="pangram_display")
                yield Static("Histogram: -", id="histogram_display")

            with Container(id="add_remove_area"):
                with Horizontal(classes="add_remove_group"):
                    yield Input(placeholder="Word to add", id="add_word_input")
                    yield Button("Add Word", id="add_word_button")
                with Horizontal(classes="add_remove_group"):
                    yield Input(placeholder="Word to remove", id="remove_word_input")
                    yield Button("Remove Word", id="remove_word_button")
        
        yield Footer()

    def on_mount(self) -> None:
        """Load word lists when the app starts."""
        self.query_one("#status_display").update("Loading word lists...")
        try:
            self.main_word_list_data = load_word_list(self.MAIN_WORDS_PATH)
            self.query_one("#status_display").update(f"Main word list loaded ({len(self.main_word_list_data)} words). Enter 7 letters to start.")
        except FileNotFoundError:
            self.query_one("#status_display").update(f"ERROR: Main word list not found at {self.MAIN_WORDS_PATH}")
            self.main_word_list_data = []
        
        try:
            self.extended_word_list_data = load_word_list(self.EXTENDED_WORDS_PATH)
        except FileNotFoundError:
            self.query_one("#status_display").renderable += f"\nWarning: Extended word list not found at {self.EXTENDED_WORDS_PATH}"
            self.extended_word_list_data = []
        
        # Initially hide extended words list and header if no data or not solved yet
        self.query_one("#extended_words_list", ListView).display = False
        self.query_one("#extended_header", Static).display = False


    def _validate_puzzle_input(self, letters: str) -> str | None:
        if not letters:
            self.query_one("#status_display").update("ERROR: Please enter 7 letters.")
            return None
        if len(letters) != 7:
            self.query_one("#status_display").update("ERROR: Please enter exactly 7 letters.")
            return None
        if not letters.isalpha():
            self.query_one("#status_display").update("ERROR: Please enter only alphabetic characters.")
            return None
        return letters.upper()

    def _validate_add_remove_input(self, word: str) -> str | None:
        if not word:
            self.query_one("#status_display").update("ERROR: Word cannot be empty.")
            return None
        if not word.isalpha():
            self.query_one("#status_display").update("ERROR: Word must contain only alphabetic characters.")
            return None
        return word.upper()

    def _format_histogram_for_display(self, hist_data: dict) -> str:
        if not hist_data:
            return "N/A"
        return length_table(hist_data)


    async def _execute_solve(self, pattern: str):
        if not self.main_word_list_data and not self.extended_word_list_data:
            self.query_one("#status_display").update("ERROR: No word lists loaded. Cannot solve.")
            return

        self.query_one("#status_display").update(f"Solving for pattern: {pattern}...")
        
        # Solve for main list
        # These are the words used for scoring and primary display
        self._current_found_words = solve(self.main_word_list_data, pattern, True, self.ADDED_WORDS_PATH, self.REMOVED_WORDS_PATH)
        
        extended_display_matches = []
        if self.extended_word_list_data:
            raw_extended = solve(self.extended_word_list_data, pattern, False) # full=False for extended
            extended_display_matches = [w for w in raw_extended if w not in self._current_found_words]

        current_pangrams = pangram(self._current_found_words, pattern)
        current_score = score(self._current_found_words, current_pangrams)
        hist_data = length_histogram(self._current_found_words)

        # Update Main Found Words List
        main_word_list_widget = self.query_one("#found_words_list", ListView)
        main_word_list_widget.clear()
        for word in self._current_found_words:
            main_word_list_widget.append(ListItem(Static(word)))
        
        # Update Extended/Bonus Words List
        extended_word_list_widget = self.query_one("#extended_words_list", ListView)
        extended_word_list_widget.clear()
        if extended_display_matches:
            for word in extended_display_matches:
                extended_word_list_widget.append(ListItem(Static(word)))
            extended_word_list_widget.display = True
            self.query_one("#extended_header", Static).display = True
        else:
            extended_word_list_widget.display = False
            self.query_one("#extended_header", Static).display = False


        self.query_one("#score_display").update(f"Score: {current_score}")
        self.query_one("#word_count_display").update(f"Words (Main): {len(self._current_found_words)}")
        self.query_one("#extended_word_count_display").update(f"Words (Extended): {len(extended_display_matches)}")
        self.query_one("#pangram_display").update(f"Pangrams: {', '.join(current_pangrams) if current_pangrams else 'None'}")
        self.query_one("#histogram_display").update(self._format_histogram_for_display(hist_data))

        status_message = f"Solved! Found {len(self._current_found_words)} main words."
        if extended_display_matches:
            status_message += f" Found {len(extended_display_matches)} extended words."
        self.query_one("#status_display").update(status_message)
        self.current_pattern = pattern

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "solve_button":
            letters_input_widget = self.query_one("#letters_input", Input)
            pattern_input = letters_input_widget.value
            valid_pattern = self._validate_puzzle_input(pattern_input)
            if valid_pattern:
                # Clear previous solution words before solving new one
                self._current_found_words = [] 
                self.query_one("#found_words_list", ListView).clear()
                self.query_one("#extended_words_list", ListView).clear()
                self.query_one("#extended_words_list", ListView).display = False
                self.query_one("#extended_header", Static).display = False
                await self._execute_solve(valid_pattern)
            else:
                letters_input_widget.focus()
        
        elif button_id == "hint_button":
            if self._current_found_words:
                hint_word = random.choice(self._current_found_words)
                self.query_one("#status_display").update(f"Hint: {hint_word}")
            else:
                self.query_one("#status_display").update("Solve the puzzle first to get a hint, or no words were found.")
        
        elif button_id == "add_word_button":
            add_input_widget = self.query_one("#add_word_input", Input)
            word_to_add = self._validate_add_remove_input(add_input_widget.value)
            if word_to_add:
                try:
                    add(word_to_add, self.ADDED_WORDS_PATH)
                    self.query_one("#status_display").update(f"'{word_to_add}' added to wordlist.")
                    add_input_widget.value = "" 
                    if self.current_pattern: 
                        self.query_one("#status_display").renderable += " Re-solving..."
                        await self._execute_solve(self.current_pattern)
                except Exception as e:
                    self.query_one("#status_display").update(f"Error adding word: {e}")
            add_input_widget.focus()

        elif button_id == "remove_word_button":
            remove_input_widget = self.query_one("#remove_word_input", Input)
            word_to_remove = self._validate_add_remove_input(remove_input_widget.value)
            if word_to_remove:
                try:
                    remove(word_to_remove, self.REMOVED_WORDS_PATH)
                    self.query_one("#status_display").update(f"'{word_to_remove}' added to removal list.")
                    remove_input_widget.value = "" 
                    if self.current_pattern: 
                        self.query_one("#status_display").renderable += " Re-solving..."
                        await self._execute_solve(self.current_pattern)
                except Exception as e:
                    self.query_one("#status_display").update(f"Error removing word: {e}")
            remove_input_widget.focus()

if __name__ == "__main__":
    app = SolverApp()
    app.run()
