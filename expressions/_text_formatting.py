# -*- coding: utf-8 -*-

"""
/***************************************************************************
 emiTools
                                 A QGIS plugin
 This plugin compiles tools used by EMI-PB

                              -------------------
        begin                : 2024-10-10
        copyright            : (C) 2024 by Alexandre Parente Lima
        email                : alexandre.parente@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = "Alexandre Parente Lima"
__date__ = "2024-10-10"
__copyright__ = "(C) 2024 by Alexandre Parente Lima"

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

import string

# List of words that must remain in lowercase in names/titles
# according to Portuguese language conventions and ABNT standards.

PT_BR_LOWERCASE_WORDS = {
    # Definite and indefinite articles
    "a",
    "o",
    "as",
    "os",
    "um",
    "uma",
    "uns",
    "umas",
    # Simple prepositions
    "de",
    "em",
    "por",
    "para",
    "com",
    "sem",
    "sob",
    "sobre",
    "até",
    "após",
    "ante",
    "contra",
    "desde",
    "entre",
    "trás",
    # Coordinating conjunctions
    "e",
    "ou",
    "mas",
    "nem",
    # Common subordinating conjunctions
    "se",
    "que",
    "porque",
    "como",
    "quando",
    "conforme",
    "embora",
    "caso",
    "enquanto",
    "logo",
    "pois",
    "porquanto",
    "salvo",
    # Contractions with articles
    "da",
    "do",
    "das",
    "dos",
    "na",
    "no",
    "nas",
    "nos",
    "à",
    "às",
    "ao",
    "aos",
    "pela",
    "pelo",
    "pelas",
    "pelos",
    # Contractions with pronouns
    "dela",
    "dele",
    "delas",
    "deles",
    "nela",
    "nele",
    "nelas",
    "neles",
    # Demonstrative contractions
    "deste",
    "desta",
    "destes",
    "destas",
    "neste",
    "nesta",
    "nestes",
    "nestas",
    "daquele",
    "daquela",
    "daqueles",
    "daquelas",
    "naquele",
    "naquela",
    "naqueles",
    "naquelas",
    # Other common contractions
    "doutro",
    "doutros",
    "doutra",
    "doutras",
    "noutro",
    "noutros",
    "noutra",
    "noutras",
    # Locution words
    "depois",
    "antes",
    "além",
    "aquém",
}

_PUNCT = set(
    '"' + "'«»“”‘’" + string.punctuation
)  # punctuation that may be attached to a word
_STRONG_PUNCT = {
    ".",
    ":",
    "!",
    "?",
    ";",
}  # punctuation that restarts capitalization in titles


def _split_affixes(token: str):
    """Separates leading and trailing punctuation from the core of the word."""
    if not token:
        return "", "", ""
    i, j = 0, len(token) - 1
    while i <= j and token[i] in _PUNCT:
        i += 1
    while j >= i and token[j] in _PUNCT:
        j -= 1
    return token[:i], token[i : j + 1], token[j + 1 :]


def _capitalize_core(core: str) -> str:
    """Capitalizes a regular word."""
    if not core:
        return core
    return core[0].upper() + core[1:].lower()


def _process_hyphenated(core: str, force_capitalize: bool, lowercase_words: set) -> str:
    """Processes hyphenated words part by part."""
    parts = core.split("-")
    out = []
    for part in parts:
        if not part:
            out.append(part)
            continue
        lw = part.lower()
        if force_capitalize or lw not in lowercase_words:
            out.append(_capitalize_core(part))
        else:
            out.append(lw)
    return "-".join(out)


def format_capitalization_logic(
    text: str, force_after_strong_punct: bool = False
) -> str:
    """
    Capitalizes names/titles according to PT-BR/ABNT rules:
      - the first word is always capitalized;
      - articles/prepositions/conjunctions remain lowercase (list);
      - after strong punctuation (.:;!?) the next word is capitalized;
      - handles hyphenated words.
    """
    if not text:
        return ""

    lower = PT_BR_LOWERCASE_WORDS

    tokens = str(text).split()
    result = []
    next_force = True

    for tok in tokens:
        lead, core, trail = _split_affixes(tok)

        if core:
            lw = core.lower()
            force_cap = next_force
            if "-" in core:
                new_core = _process_hyphenated(core, force_cap, lower)
            else:
                if force_cap or lw not in lower:
                    new_core = _capitalize_core(core)
                else:
                    new_core = lw
        else:
            new_core = core

        result.append(f"{lead}{new_core}{trail}")

        # ABNT: restarts capitalization after strong punctuation (in titles)
        if force_after_strong_punct and any(ch in _STRONG_PUNCT for ch in tok):
            next_force = True
        else:
            next_force = False

    return " ".join(result)
