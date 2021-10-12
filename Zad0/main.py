import json
import sys


class Automaton:

    def __init__(self, desc):
        # We don't need to remember the alphabet and states (because we assume all of the data is correct)
        self._initial = desc["initial"]
        self._accepting = desc["accepting"]
        # This form makes state update easy
        self._transitions = {(transition["letter"], transition["from"]): transition["to"]
                             for transition in desc["transitions"]}
        self._current_state = self._initial

    def update_current_state(self, letter):
        self._current_state = self._transitions[(letter, self._current_state)]

    def is_accepting(self):
        return self._current_state in self._accepting

    def reset(self):
        # Used to reset automaton state after finishing a word
        self._current_state = self._initial


def main():
    path = sys.stdin.readline().strip()
    with open(path, "r") as f:
        automaton = Automaton(json.load(f))
    while True:
        # We need to process the input byte by byte
        letter = sys.stdin.read(1)
        if not letter:
            # EOF results in letter=''
            break
        else:
            if letter == '\n':
                # Word is finished
                print("yes" if automaton.is_accepting() else "no")
                automaton.reset()
            else:
                # We are still processing current word
                automaton.update_current_state(letter)


main()
