import json
import random
import re
import sys

from collections import defaultdict
from itertools import chain

import pyphen


def split_syllables(name):
    dictionary = pyphen.Pyphen(lang="en")

    words = [w + " " for w in name.lower().split(" ")]
    syllables = map(dictionary.inserted, words)
    flattened_map = chain(*[w.split("-") for w in syllables])

    return list(flattened_map)


def build_markov_chain(names):
    def append_endmarker(syllables):
        syllables.append(0)
        return syllables

    syllables = map(split_syllables, names)
    syllables = map(append_endmarker, syllables)

    start_syllables = [w[0] for w in syllables]
    markov_chain = defaultdict(list)

    for name in syllables:
        for i, syllable in enumerate(name):
            if syllable != 0 and name[i+1] not in markov_chain[syllable]:
                markov_chain[syllable].append(name[i+1])

    return (start_syllables, markov_chain)


def generate_name(start, markov_chain, max_words=2):
    while True:
        if isinstance(start, list):
            next_syllable = random.choice(start)
        else:
            next_syllable = start

        new_name = next_syllable

        while True:
            next_syllable = random.choice(markov_chain[next_syllable])

            if next_syllable == 0:
                break
            else:
                new_name += next_syllable

        new_name = new_name.strip()

        if len(new_name.split(" ")) <= max_words:
            break

    new_name = " ".join([word.capitalize() for word in new_name.split(" ")])
    return new_name


def name_exists(name, names):
    return name.lower() in names


def main():
    num_names = 1
    input_names = []

    if len(sys.argv) >= 2:
        num_names = int(sys.argv[1])

    with open("data/cities.json", "r") as data_file:
        data = json.load(data_file)
        data = data['results']['bindings']

        for row in data:
            name = row['name']['value']
            name = name.split(',')[0].lower()
            name = re.sub("[^a-z ]", "", name)

            input_names.append(name)

    start_syllables, markov_chain = build_markov_chain(input_names)
    generated_names = set()

    while len(generated_names) < num_names:
        new_name = generate_name(start_syllables, markov_chain)

        if not name_exists(new_name, input_names):
            generated_names.add(new_name)

    for name in generated_names:
        print name


if __name__ == "__main__":
    main()
