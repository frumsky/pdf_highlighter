import re

import itertools



prox_pattern = r'( [Ww]/[0-9] | [Ww]/[0-9][0-9] )'


def remove_special(line):
    line = line.strip()
    line = re.sub(r'\"|\(|\)', '', line)
    line = re.sub(r'(\||\+|\/|\.)', r'[\1]', line)
    line = re.sub(r' OR ', '|', line)
    line = re.sub(r'\*', r'\\S*', line)
    line = line.strip()

    return line

def handle_prox(line):
    operators = []

    split_list = re.split(prox_pattern, line)

    for index, operator in enumerate(split_list):
        if re.match(prox_pattern, operator):
            operators.append((index, operator))


    remove_operators = lambda tup : split_list.remove(tup[1])

    list(map(remove_operators, operators))

    for index, i in enumerate(split_list):
        split_list[index] = remove_special(i)
    
    permutated_list = itertools.permutations(split_list)

    permutations = []
    for permutation in permutated_list:
        permutation = list(permutation)
        reinsert_operators = lambda tup : permutation.insert(tup[0], tup[1])
        list(map(reinsert_operators, operators))
        permutations.append(permutation)

    for index, permutation in enumerate(permutations):
        permutations[index] = ''.join(permutation)
        permutations[index] = re.sub(r' [Ww]/([0-9]|[0-9][0-9]) ', r'\\W+(?:\\w+\\W+){0,\1}?', permutations[index])
        
    return '|'.join(permutations)
        
    

def parse_queries(txt_file):
    queries = []
    with open(txt_file, 'r', encoding='utf-8') as r:
        lines = r.readlines()
        for line in lines:
            queries.append(line)

    for index, query in enumerate(queries):

        try:
            if re.search(prox_pattern, query):
                queries[index] = r'\b' + handle_prox(query) + r'\b'
            else:
                queries[index] = r'\b' + remove_special(query) + r'\b'
        except TypeError as e:
            print(query)
            print(e)
    
    for index, query in enumerate(queries):
        queries[index] = re.compile(query, flags=re.I + re.M)

    return [query for query in queries]
        