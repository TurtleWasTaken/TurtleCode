def wordNum_charIndex(string: str, word_num: int, separators: list = None):
    if separators is None:
        separators = [" "]
    return len(" ".join(big_split(string, separators)[:word_num]))


def charIndex_wordNum(string: str, char_index: int, separators: list = None):
    if separators is None:
        separators = [" "]
    return len(big_split(string[:char_index], separators))-1


def charIndex_lineNum(string: str, char_index: int):
    return len(string[:char_index].split("\n")) - 1


def lineNum_charIndex(string: str, line_num: int):
    return len("".join(string.split("\n")[:line_num]))


def big_split(string: str, separators: list):

    for sep in separators:
        string = string.replace(sep, separators[0])

    return string.split(separators[0])


def big_search(string: str, search_for: str):

    out = []

    for char_num in range(len(string)):

        if string[char_num:char_num+len(search_for)] == search_for:
            out.append(char_num)

    return out


def replace_string_at(string: str, start_ind: int, end_ind: int, replace_with: str):
    char_list = list(string)
    r_char_list = list(replace_with)

    char_list[start_ind:end_ind] = r_char_list

    out = "".join(char_list)

    return out

