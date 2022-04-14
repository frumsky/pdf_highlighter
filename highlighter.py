#!/usr/bin/env python
# -*- coding: utf-8 -*-
from parser import parse_queries
from text_extractor import convert_pdf_to_txt
import os
import fitz
from tqdm import tqdm
import time
import re2 as re
from pathlib import Path
from pdfminer.pdfparser import PDFSyntaxError
from multiprocessing import Pool


def get_search_hits(pattern_sets, document):
    doc_name = document.split('/')[-1].replace('.pdf', '')
    
    strings = set()

    text = convert_pdf_to_txt(document)
    
    for pattern in pattern_sets:
        match = re.finditer(pattern, text)
        match = list(match)

        if not match:
            continue
        print('\n')
        print('Document: ', document)
        print('Pattern: ', pattern)
        print('Match: ', match)
        print('\n')

        matches = [i.group() for i in match]
        for i in list(matches) : strings.add((i))
    


    return list(strings)

def validate(page, term):
    try:
        hit = page.search_for(term)
    except TypeError as e:
        print('ERROR:')
        print(term)
        print(e)
        print('\n')
    # if not re.search(term, page.get_textbox(hit)):
    #     return
    # else:
    #     return hit

    return hit

def highlight_hits(terms, document):
    highlighted = False
    doc = fitz.open(document)
    pages = [doc[i] for i in range(0, doc.page_count)]

    for page in pages:
        find_hits = lambda x : validate(page, x)
        hits = list(map(find_hits, terms))
        for hit in hits:
            if not hit:
                continue
            highlighted = True
            page.add_highlight_annot(hit)

    if highlighted:
        doc.save("%s_HIGHLIGHTED.pdf"%document, garbage=4, deflate=True, clean=True, ascii=True)

def wrapper(tup):
    query_file = tup[0]
    document = tup[1]

    queries = parse_queries(query_file)

    try:
        search_terms = get_search_hits(queries, document)
        highlight_hits(search_terms, document)
    except (UnboundLocalError, PDFSyntaxError) as e:
        pass

def run_highlighter(st_path, dir):
    files = os.listdir(dir)
    files = [(st_path, os.path.join(dir, i)) for i in files]

    with Pool(processes=3) as pool:
        pool.map_async(wrapper, files)
        pool.close()
        pool.join()

if __name__ == '__main__':
    search_file = '/Users/frankchlumsky/Downloads/Taiwan_Export_14/Native/Search/terms.txt'
    documents_path = '/Users/frankchlumsky/Downloads/Taiwan_Export_14/Native/FLD0001'
    run_highlighter(search_file, documents_path)



# string = '''/Users/frankchlumsky/Desktop/Desktop - MacBook Pro (2)/Work/Novartis/Tools/Portugal/Products_Portugal.txt'''
# queries = parse_queries(string)

# directory = '/Users/frankchlumsky/Downloads/TEST'
# files = os.listdir(directory)
# files = [os.path.join(directory, i) for i in files]

# for file in files:
#     try:
#         search_terms = get_search_hits(queries, file)
#         highlight_hits(search_terms, file)
#     except:
#         pass

# doc = '''/Users/frankchlumsky/Downloads/TEST/0023.pdf'''

# search_terms = get_search_hits(queries, doc)

# highlight_hits(search_terms, doc)
