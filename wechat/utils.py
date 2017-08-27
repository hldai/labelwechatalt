def load_names_file(filename):
    f = open(filename, 'r')
    names = set()
    for line in f:
        names.add(line.strip().decode('utf-8'))
    f.close()
    return names


def fix_jieba_words(words):
    words_list = list()
    for w in words:
        w = w.strip()
        if w:
            words_list.append(w)
    return words_list
