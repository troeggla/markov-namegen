import json
import random
import re
import sys

from collections import defaultdict
from split_syllables import split_syllables


def build_markov_chain(names):
    def append_endmarker(s):
        s.append(0)
        return s

    syllables = map(split_syllables, names)
    syllables = map(append_endmarker, syllables)

    start_syllables = map(lambda w: w[0], syllables)
    markov_chain = defaultdict(list)

    for name in syllables:
        if len(name) == 2:
            next

        for i, syllable in enumerate(name):
            if syllable != 0 and name[i+1] not in markov_chain[syllable]:
                markov_chain[syllable].append(name[i+1])

    return (start_syllables, markov_chain)


def generate_name(start_syllables, markov_chain):
    while True:
        next_syllable = random.choice(start_syllables)
        new_name = next_syllable

        while True:
            next_syllable = random.choice(markov_chain[next_syllable])

            if next_syllable == 0:
                break
            else:
                new_name += next_syllable

        new_name = new_name.strip()

        if len(new_name.split(" ")) < 3:
            break

    new_name = " ".join([word.capitalize() for word in new_name.split(" ")])
    return new_name


def name_exists(name, names):
    return name.lower() in names


if __name__ == "__main__":
    num_names = 1

    if len(sys.argv) >= 2:
        num_names = int(sys.argv[1])

    names = []

    with open("cities.json", "r") as f:
        data = json.load(f)
        data = data['results']['bindings']

        names = map(lambda row: row['name']['value'], data)
        names = map(lambda name: name.split(',')[0].lower(), names)
        names = map(lambda name: re.sub("[^a-z ]", "", name), names)

    start_syllables, markov_chain = build_markov_chain(names)
    generated_names = set()

    while len(generated_names) < num_names:
        new_name = generate_name(start_syllables, markov_chain)

        if not name_exists(new_name, names):
            generated_names.add(new_name)

    for name in generated_names:
        print name
