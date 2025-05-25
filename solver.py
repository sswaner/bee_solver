from sys import argv
import textwrap
import random

from tabulate import tabulate

# f = open("./wordlists/words.txt") # Will be removed

def load_word_list(filepath: str) -> list[str]:
    """Loads words from a file, strips whitespace, and converts to uppercase."""
    words = []
    with open(filepath, 'r') as file:
        for line in file:
            words.append(line.strip().upper())
    return words

def length_table(data):
    # Create a set of all possible keys from inner dictionaries (column headers)
    columns = set()
    for inner_dict in data.values():
        columns.update(inner_dict.keys())
    columns = sorted(columns)

    # Prepare the list for tabulate
    table_data = []
    for key, inner_dict in data.items():
        row = [key] + [inner_dict.get(col, '-') for col in columns]
        table_data.append(row)

    # Print the table using tabulate
    headers = ["Key"] + [str(col) for col in columns]
    return tabulate(table_data, headers=headers, tablefmt="plain")

def solve(word_list: list[str], input_string: str, full: bool = True, added_words_path: str = "wordlists/added_words.txt", removed_words_path: str = "wordlists/removed_words.txt") -> list[str]:
    results = []
    # count = 0 # count was unused
    c = input_string[0]
    for word_entry in word_list: # Changed 'words' to 'word_list' to avoid confusion with the module name
        w = word_entry # Already upper from load_word_list
        match = False
        if len(w) < 4:
            continue #too short
        if c in w:
            match = True
            for l in w:
                if l not in input_string:
                    match = False
                    break # More efficient to break once a non-matching character is found
            if match:
                results.append(w)
    # add words
    if full:
        try:
            added_word_entries = load_word_list(added_words_path)
            # The recursive call to solve here should not pass `full=True` again,
            # and it should operate on the specifically loaded added_word_entries.
            # Also, it should not try to load added/removed words again.
            added_matches = solve(added_word_entries, input_string, False, added_words_path, removed_words_path)
            if added_matches:
                for item in added_matches: # Changed 'match' to 'item' to avoid conflict
                    if item not in results: # Ensure no duplicates if added words are also in main list
                        results.append(item)
        except FileNotFoundError:
            # If added_words.txt doesn't exist, it's not an error, just means no added words.
            pass

    # remove words
    try:
        removed_word_entries = load_word_list(removed_words_path)
        # Create a set for efficient lookup
        removed_set = set(removed_word_entries)
        results = [r for r in results if r not in removed_set]
    except FileNotFoundError:
        # If removed_words.txt doesn't exist, it's not an error.
        pass

    return sorted(results)

# The search function seems unused by the main CLI logic and might be obsolete or for other purposes.
# For now, I'll leave it but ensure it uses load_word_list if it were to be used.
# However, its current implementation reads from a global 'words' which is problematic.
# Given the refactoring goals, this function should ideally also take a word_list as argument.
# Since it's not directly part of the current task's core functions to refactor for the TUI,
# I will comment it out to avoid issues with the global 'words' that will be removed.
# If it's needed later, it should be refactored properly.
# def search(filename, input_string, exact_match = True):
#     # word_data = load_word_list('./{0}'.format(filename)) # Example of how it would load
#     matches = []
#     # for word_entry in word_data: # Corrected loop
#     #     if exact_match:
#     #         if input_string == word_entry:
#     #             # words.close() # Not needed with load_word_list
#     #             return ([word_entry], True)
#     #     else:
#     #         if input_string in word_entry:
#     #             matches.append(word_entry)
#     # words.close() # Not needed
#     return (matches, False)

def pangram(found_words: list[str], input_string: str) -> list[str]:
    i = set(input_string.upper()) # Ensure input_string is uppercase for comparison
    results = []
    for word in found_words: # Iterate over already found_words
        # w = set(word.strip()) # .strip() is already handled by load_word_list
        w = set(word) # word is already stripped and upper
        if w == i:
            results.append(word)
    return results

def score(found_words: list[str], pangrams_list: list[str]) -> int:
    total_score = 0
    pangrams_set = set(pangrams_list) # For efficient lookup
    for word in found_words:
        current_score = 0
        if len(word) == 4:
            current_score = 1
        else:
            current_score = len(word) # .strip() already handled
        if word in pangrams_set:
            current_score += 7
        total_score += current_score
    return total_score

def length_histogram(matches: list[str]) -> dict:
    length_list = {}
    # table_widths = [3, 2, 2, 2, 2, 2, 2, 2, 2, 2] # Not needed if returning dict

    for word in matches:
        key = word[:1]
        # length_string = len(word.strip()) # .strip() already handled
        word_len = len(word)
        sub_key = length_list.get(key, {})
        table_value = sub_key.get(word_len, 0) + 1
        sub_key[word_len] = table_value
        length_list[key] = sub_key

    # final_table = length_table(length_list) # TUI will handle formatting
    return length_list



def histogram(matches):

    table_widths = [3, 2, 2, 2, 2, 2, 2, 2, 2, 2]

    slug_list = {}

    for word in matches:
        slug = word[:1]
        if slug in slug_list:
            slug_list[slug] += 1
        else:
            slug_list[slug] = 1
    
    long_slugs = [k for k,v  in slug_list.items() if v > 3]
    
    #for (k, v) in long_slugs:
    for word in matches:
        if word[:1] in long_slugs:
            slug = word[:2]
            if slug in slug_list:
                slug_list[slug] += 1
            else:
                slug_list[slug] = 1
    
    length_list = {}    

    for word in matches:
        key = word[:1]
        length_string = len(word.strip())
        sub_key = length_list.get(key, {})

        sub_key[length_string] = sub_key.get(length_string, 0) + 1
        length_list[key] = sub_key


    return slug_list

def display(pattern, matches, extended_matches = None):
    
    length_histogram_widths = [3, 2, 2, 2, 2, 2, 2, 2, 2, 2]    

    matches_str = ', '.join(matches)
    table = []
    all_words = textwrap.wrap( ', '.join(matches), 64)
    table.append(["All Words", textwrap.fill(matches_str)])
    table.append(['Count', len(matches)])
    current_pangrams = pangram(matches, pattern) # Use refactored pangram
    pangrams_text = textwrap.fill(', '.join(current_pangrams))
    table.append(['Pangrams', pangrams_text])
    table.append(['Histogram', textwrap.fill(str(histogram(matches)))]) # histogram() is not yet refactored to return raw data
    
    # For length_histogram, call the refactored version and then format it using length_table for CLI display
    raw_length_hist = length_histogram(matches)
    table.append(['Length Histogram', length_table(raw_length_hist)]) # Format raw data for CLI
    
    table.append(['Score', score(matches, current_pangrams)]) # Use refactored score
    if extended_matches:
        extended_text = textwrap.fill(', '.join(extended_matches))
        table.append(['Extended Matches({0})'.format(len(extended_matches)), extended_text])

    headers = ['Section', 'Results']
    print(tabulate(table, headers, tablefmt="grid"))

def show_menu(pattern=None):
    if not pattern:
    o = input("Enter 7 characters: ").upper() # Pattern is already upper, this might be redundant or for a different context
    
def add(word: str, added_words_path: str = "wordlists/added_words.txt"):
    with open(added_words_path, "a+") as f: # Use with statement
        f.write(word.upper()) # Ensure word is uppercase
        f.write("\n")
    # f.close() # Not needed with "with"

def remove(word: str, removed_words_path: str = "wordlists/removed_words.txt"):
    with open(removed_words_path, "a+") as f: # Use with statement
        f.write(word.upper()) # Ensure word is uppercase
        f.write("\n")
    # f.close() # Not needed with "with"

def solve_puzzle(pattern: str, main_word_list: list[str], extended_word_list: list[str]):
    # Removed direct file opening, expects loaded lists
    matches = solve(main_word_list, pattern, True)
    # extended = [w for w in solve(extended_word_list, pattern, True) if w not in matches]
    # For extended words, we should not use full=True as it would try to load added/removed lists again
    # and potentially based on default paths.
    # Also, the solve function itself handles added/removed words if `full=True`.
    # If the intention for 'extended' is purely words from xwi_bee_words not in the primary solution (including added words),
    # then the logic needs to be:
    # 1. Solve for main_word_list (this includes added words if full=True).
    # 2. Solve for extended_word_list (with full=False, so it doesn't re-add/re-remove).
    # 3. Find words in the result of step 2 that are not in the result of step 1.

    # Let's refine extended logic:
    # 'matches' already contains words from main_word_list + added_words - removed_words.
    # We want words from extended_word_list that are valid for the pattern AND are not in 'matches'.
    
    # Solve with the extended list, but without applying added/removed logic from files again.
    # So, full=False is appropriate here.
    raw_extended_matches = solve(extended_word_list, pattern, False)
    extended_display_matches = [w for w in raw_extended_matches if w not in matches]
    
    display(pattern, matches, extended_display_matches)

if __name__ == "__main__":
    #option = show_menu() # show_menu seems to only get input, not used for options
    command = 'solve'
    # Define default file paths, can be overridden if needed
    main_words_file = "./wordlists/words.txt"
    extended_words_file = 'wordlists/xwi_bee_words.txt'
    added_words_file = 'wordlists/added_words.txt'
    removed_words_file = 'wordlists/removed_words.txt'

    # Load main word lists once
    main_word_list_data = load_word_list(main_words_file)
    extended_word_list_data = load_word_list(extended_words_file)

    commands = ['solve', 'hint', 'add', 'remove', 'dump', 'pangram', 'puzzle'] # Added 'puzzle' for solve_puzzle

    cli_pattern = "" # Initialize pattern

    if len(argv) == 2:
        if argv[1].lower() not in commands: # Make command check case-insensitive
            # If the second arg is not a command, assume it's a pattern for 'solve'
            command = 'solve' # Default to solve if not specified
            cli_pattern = argv[1]
            # print(f"Solving for pattern: {cli_pattern}")
        else:
            # It's a command, but no pattern provided yet
            command = argv[1].lower()
            if command not in ['add', 'remove']: # These commands take the pattern as the word to add/remove
                 cli_pattern = input("Enter 7 characters: ").upper()
            else: # For add/remove, the "pattern" is the word itself
                cli_pattern = input(f"Enter word to {command}: ").upper()

    elif len(argv) == 3:
        command = argv[1].lower()
        cli_pattern = argv[2] # Pattern or word for add/remove
    else: # Default behavior if no args or only script name
        cli_pattern = input("Enter 7 characters: ").upper()


    cli_pattern = cli_pattern.upper()

    if command == 'solve':
        # Pass loaded lists to solve. `solve` handles added/removed words internally if full=True.
        current_matches = solve(main_word_list_data, cli_pattern, True, added_words_file, removed_words_file)
        # For extended, we want words from extended_word_list_data that are valid for the pattern
        # AND are not already in current_matches (which includes added words).
        # We call solve with full=False for the extended list so it doesn't re-process added/removed files.
        raw_extended = solve(extended_word_list_data, cli_pattern, False)
        extended_display = [w for w in raw_extended if w not in current_matches]
        display(cli_pattern, current_matches, extended_display)
    elif command == 'puzzle': # A dedicated command for the original solve_puzzle behavior
        solve_puzzle(cli_pattern, main_word_list_data, extended_word_list_data)
    elif command == 'hint':
        # Hints should come from the main word list solution
        current_matches = solve(main_word_list_data, cli_pattern, True, added_words_file, removed_words_file)
        if current_matches:
            print("Try: ", random.choice(current_matches))
        else:
            print("No matches found for a hint.")
    elif command == 'add':
        # Here, cli_pattern is the word to add
        add(cli_pattern.strip(), added_words_file)
        print(f"Added '{cli_pattern.strip()}' to the added words list.")
    elif command == 'remove':
        # Here, cli_pattern is the word to remove
        remove(cli_pattern.strip(), removed_words_file)
        print(f"Added '{cli_pattern.strip()}' to the removed words list.")
    elif command == 'pangram':
        current_matches = solve(main_word_list_data, cli_pattern, True, added_words_file, removed_words_file)
        current_pangrams = pangram(current_matches, cli_pattern)
        print('Pangram(s): ', ", ".join(current_pangrams) if current_pangrams else "None found")
    elif command == "dump": # This command's purpose seems to be to remove all extended words found
        # First, find all matches from the main list (including added/removed)
        main_matches = solve(main_word_list_data, cli_pattern, True, added_words_file, removed_words_file)
        # Then, find all valid words from the extended list (without applying added/removed logic again)
        extended_candidates = solve(extended_word_list_data, cli_pattern, False)
        
        words_to_remove_from_game = []
        for word in extended_candidates:
            if word not in main_matches: # Only consider words that aren't part of the "standard" solution
                words_to_remove_from_game.append(word)
                
        if words_to_remove_from_game:
            print(f"Identified {len(words_to_remove_from_game)} words from the extended list (not in main solution) to add to removed_words.txt:")
            for word in words_to_remove_from_game:
                print(f"  Adding '{word.strip()}' to removed list.")
                remove(word.strip(), removed_words_file) # Use the remove function
            print("Dump operation complete. These words will be excluded from future solves.")
        else:
            print("No words found in the extended list (that are not in the main solution) to dump.")
    else:
        print(f"Unknown command: '{command}'. Valid commands are: {', '.join(commands)}")
