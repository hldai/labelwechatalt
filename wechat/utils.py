def load_names_file(filename):
    f = open(filename, 'r')
    names = set()
    for line in f:
        names.add(line.strip().decode('utf-8'))
    f.close()
    return names
