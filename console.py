import solver
from solver import f

puzzle = ''

def extract_param(command, input_string):
    return input_string.replace(command, '').strip()


def command_line(puzzle):
    if puzzle == '':
        cmd = input(">")
    else:
        cmd = input("({0}) >".format(puzzle))
    if cmd.startswith('='):
        set_puzzle_to = extract_param('=', cmd)
        if set_puzzle_to != '':
            puzzle = set_puzzle_to
        else:
            print("No puzzle string entered")
        print("Set the daily puzzle to {0}".format(puzzle))
    elif cmd.startswith('+'):
        added_word = extract_param('+', cmd)
        solver.add(added_word)
        print("Added word: ", added_word)
    elif cmd.startswith('-'):

        print("remove a word")
    elif cmd.startswith(':s'):
        print("solve {0}".format(cmd.replace(':s', '').strip()))
        solver.solve_puzzle(puzzle)
    elif cmd.startswith(':p'):
        print("show pangrams {0}".format(cmd.replace(':p', '').strip()))
    elif cmd.startswith(':x'):
        exit()
    else:
        print("unknown command")
    return puzzle

if __name__ == '__main__':
    puzzle = ''
    while True:
        puzzle = command_line(puzzle.upper())
