def wordNum_charIndex(string: str, word_num: int):
    return len(" ".join(string.split()[:word_num]))
