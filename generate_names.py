""" Generate fictional town names using a Markov chain.

This file uses a list of US towns as input, splits each name into syllables and
uses those to build a Markov chain, which can be used to generate fictional
town names.

Normally, this script should be called from the command line, optionally
passing in the number of names to be generated. If no arguments are passed to
the script, a single name is generated.
"""

import json
import random
import re
import sys

from collections import defaultdict
from itertools import chain

import pyphen


def split_syllables(name):
    """ Splits a given string into syllables.

    This function takes a word, or a sequence of words and splits it into its
    corresponding syllables. The syllables are returned in a list, which each
    syllable in lowercase. A syllable with a space at the end indicates that
    this syllable marks the end of a word.
    """
    dictionary = pyphen.Pyphen(lang="en")

    # Convert to lower-case and split words
    words = [w + " " for w in name.lower().split(" ")]
    # Hyphenate words
    syllables = map(dictionary.inserted, words)
    # Split at hyphenation points and flatten list
    flattened_map = chain(*[w.split("-") for w in syllables])

    return list(flattened_map)


def build_markov_chain(names):
    """ Builds a Markov chain given a list of names.

    Takes a list of names, each of which is split into syllables and builds a
    Markov chain from it. The function returns a tuple containing a list of
    syllables which can be used to start new names and the Markov chain as a
    dictionary.
    """
    def append_endmarker(syllables):
        """ Appends 0 to a list of syllables, marking the end of a name. """
        syllables.append(0)
        return syllables

    syllables = map(split_syllables, names)
    syllables = map(append_endmarker, syllables)

    # Get first syllable of each name as start syllable
    start_syllables = [w[0] for w in syllables]
    markov_chain = defaultdict(list)

    for name in syllables:
        for i, syllable in enumerate(name):
            # Check if syllable is not end marker and next syllable is not
            # already in the chain
            if syllable != 0 and name[i+1] not in markov_chain[syllable]:
                markov_chain[syllable].append(name[i+1])

    # Return tuple of start syllables and generated Markov chain
    return (start_syllables, markov_chain)


def generate_name(start, markov_chain, max_words=2):
    """ Generates a new town name, given a start syllable and a Markov chain

    This function takes a single start syllable or a list of start syllables,
    one of which is then chosen randomly, and a corresponding Markov chain to
    generate a new fictional town name. The number of words in the name can
    optionally be passed in as an argument and defaults to 2 otherwise.

    Note that it is possible that the generated name already exists. To avoid
    that, one should check whether the name exists against the set of input
    names.
    """
    while True:
        if isinstance(start, list):
            # If start is a list choose a syllable randomly
            next_syllable = random.choice(start)
        else:
            next_syllable = start

        # Initialise new name
        new_name = next_syllable

        while True:
            # Choose next syllable from the Markov chain
            next_syllable = random.choice(markov_chain[next_syllable])

            # Return if end of word has been reached
            if next_syllable == 0:
                break
            else:
                new_name += next_syllable

        # Remove leading and trailing spaces
        new_name = new_name.strip()

        # Make sure name has less words than max_words, otherwise start over
        if len(new_name.split(" ")) <= max_words:
            break

    # Capitalise every word in the new name
    new_name = " ".join([word.capitalize() for word in new_name.split(" ")])
    return new_name


def name_exists(name, names):
    """ Check if a given name exists in a set of existing names. """
    return name.lower() in names


def main():
    """ Reads the input file and generates a set of unique fictional names.

    This function is invoked automatically if the script is called from the
    command line. It reads the set of input names from data/cities.json, which
    contains about 9000 city/place names in the US, builds a Markov chain and
    generates a unique set of unique new names, which are not contained in the
    input set. The number of names to be generated can be passed in through
    the command line and defaults to 1 otherwise.

    After successfully generating the specified number of names, they are
    printed line by line onto the standard output.
    """
    num_names = 1
    input_names = []

    # Check if a name count has been passed in
    if len(sys.argv) >= 2:
        num_names = int(sys.argv[1])

    with open("data/cities.json", "r") as data_file:
        # Load and parse file
        data = json.load(data_file)
        data = data['results']['bindings']

        for row in data:
            name = row['name']['value']
            # Remove name of US state
            name = name.split(',')[0].lower()
            # Remove everything which is not a letter or a space
            name = re.sub("[^a-z ]", "", name)

            input_names.append(name)

    # Build Markov chain
    start_syllables, markov_chain = build_markov_chain(input_names)
    generated_names = set()

    # Repeat until we have the desired number of names
    while len(generated_names) < num_names:
        # Generate new name
        new_name = generate_name(start_syllables, markov_chain)

        # Make sure generated name does not exist already
        if not name_exists(new_name, input_names):
            generated_names.add(new_name)

    # Print generated names line by line
    for name in generated_names:
        print name


if __name__ == "__main__":
    # Call main() if script has been launched from the command line
    main()
