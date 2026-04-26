"""
Transliterator to map English formulas and common Latin words to Amharic phonetic text
so that the Meta MMS Amharic TTS model can read them properly instead of emitting static/garbage.
"""

import re

LATIN_TO_AMHARIC_MAP = {
    "A": "ኤ", "B": "ቢ", "C": "ሲ", "D": "ዲ", "E": "ኢ", "F": "ኤፍ", "G": "ጂ", 
    "H": "ኤች", "I": "አይ", "J": "ጄ", "K": "ኬ", "L": "ኤል", "M": "ኤም", "N": "ኤን", 
    "O": "ኦ", "P": "ፒ", "Q": "ኪው", "R": "አር", "S": "ኤስ", "T": "ቲ", 
    "U": "ዩ", "V": "ቪ", "W": "ደብሊው", "X": "ኤክስ", "Y": "ዋይ", "Z": "ዜድ",
    "a": "ኤ", "b": "ቢ", "c": "ሲ", "d": "ዲ", "e": "ኢ", "f": "ኤፍ", "g": "ጂ", 
    "h": "ኤች", "i": "አይ", "j": "ጄ", "k": "ኬ", "l": "ኤል", "m": "ኤም", "n": "ኤን", 
    "o": "ኦ", "p": "ፒ", "q": "ኪው", "r": "አር", "s": "ኤስ", "t": "ቲ", 
    "u": "ዩ", "v": "ቪ", "w": "ደብሊው", "x": "ኤክስ", "y": "ዋይ", "z": "ዜድ",
    "=": "እኩል ነው",
    "+": "ሲደመር",
    "-": "ሲቀነስ",
    "*": "ሲባዛ",
    "/": "ሲካፈል",
    "^2": "ስኩዌር",
    "^": "ዘ ፓወር ኦፍ",
    "0": "ዜሮ", "1": "አንድ", "2": "ሁለት", "3": "ሶስት", "4": "አራት", "5": "አምስት", 
    "6": "ስድስት", "7": "ሰባት", "8": "ስምንት", "9": "ዘጠኝ",
    "cos": "ኮስ",
    "sin": "ሳይን",
    "tan": "ታን",
    "theta": "ቴታ",
    "alpha": "አልፋ",
    "beta": "ቤታ",
    "gamma": "ጋማ"
}

def clean_amharic_tts_text(text: str) -> str:
    """Prepares text for Meta MMS Amharic by replacing Latin letters and math symbols."""
    # First replace multi-character specific tokens
    for k, v in [("^2", "ስኩዌር"), ("cos", "ኮስ"), ("sin", "ሳይን"), ("tan", "ታን"), 
                 ("theta", "ቴታ"), ("alpha", "አልፋ"), ("beta", "ቤታ"), ("gamma", "ጋማ")]:
        text = text.replace(k, f" {v} ")
    
    # Process character by character for isolated latin letters/math
    new_text = []
    for char in text:
        if char in LATIN_TO_AMHARIC_MAP:
            new_text.append(f" {LATIN_TO_AMHARIC_MAP[char]} ")
        else:
            new_text.append(char)
            
    # Clean up double spaces
    result = "".join(new_text)
    result = re.sub(r'\s+', ' ', result).strip()
    return result
