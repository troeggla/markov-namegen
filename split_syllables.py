import pyphen
from itertools import chain


def split_syllables(name):
    dictionary = pyphen.Pyphen(lang="en")

    words = map(lambda w: w + " ", name.lower().split(" "))
    syllables = map(lambda w: dictionary.inserted(w), words)
    flattened_map = chain(*map(lambda w: w.split("-"), syllables))

    return list(flattened_map)
