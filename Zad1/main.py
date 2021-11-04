import json
import sys


def yield_state_name():
    i = 1
    while True:
        i += 1
        yield f'q{i}'


class Automaton:
    def __init__(self):
        self._transitions = {}
        self._initial = "q1"
        self._accepting = set()
        self._alphabet = set()
        self._states = {self._initial}
        self._current_state = self._initial
        self._names_generator = yield_state_name()
        self.is_current_word_in_language = None

    def __str__(self):
        # Parses automaton to expected json format
        parsed_transitions = self._parse_transitions()
        automaton_json = {
            "alphabet": list(self._alphabet),
            # Sorting for readability
            "states": sorted(list(self._states)),
            "initial": self._initial,
            # Sorting for readability
            "accepting": sorted(list(self._accepting)),
            "transitions": parsed_transitions
        }
        return json.dumps(automaton_json, indent=4)

    def _parse_transitions(self):
        # Parses transitions to expected json format and updated alphabet and states sets.
        parsed_transitions = []
        for k, v in self._transitions.items():
            self._alphabet.add(k[0])
            self._states.add(v)
            parsed_transitions.append({"letter": k[0], "from": k[1], "to": v})
        return parsed_transitions

    def finish_word(self):
        # Does few sanity checks, adds current state to accepting states if the word should be accepted and prepares
        # automaton for new word.
        assert self.is_current_word_in_language is not None, "When finishing word, we must know whether this word " \
                                                             "should be accepted or not. "
        if not self.is_current_word_in_language:
            assert self._current_state not in self._accepting, "If word should not be accepted, last state it reaches " \
                                                               "should not be in accepting states. "
        if self.is_current_word_in_language:
            self._accepting.add(self._current_state)
        self._current_state = self._initial
        self.is_current_word_in_language = None

    def update(self, letter):
        # If there exits suitable transition, uses it. Otherwise, adds new transition and state.
        if (possible_next_state := self._transitions.get((letter, self._current_state))) is not None:
            self._current_state = possible_next_state
        else:
            new_state_name = next(self._names_generator)
            self._transitions[(letter, self._current_state)] = new_state_name
            self._current_state = new_state_name


def main():
    automaton = Automaton()
    words_count = int(input())
    for _ in range(words_count):
        while True:
            # We need to process the input byte by byte
            letter = sys.stdin.read(1)
            # Assumption: + and - are not members of alphabet
            if letter == '+':
                automaton.is_current_word_in_language = True
            elif letter == '-':
                automaton.is_current_word_in_language = False
            elif letter == '\n':
                automaton.finish_word()
                break
            else:
                automaton.update(letter)
    print(automaton)


main()
