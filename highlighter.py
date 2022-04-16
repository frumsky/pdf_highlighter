#!/usr/bin/env python
# -*- coding: utf-8 -*-
from parser import parse_queries
from text_extractor import convert_pdf_to_txt
import os
import fitz
from tqdm import tqdm
import time
from datetime import datetime
import re2 as re
from pathlib import Path
from pdfminer.pdfparser import PDFSyntaxError
from multiprocessing import Pool
from concurrent import futures

def match_pattern(text, pattern, doc_name):
    match = re.finditer(pattern, text)
    match = list(match)
    if not match:
        return
    print('\n')
    print('Document: ', doc_name)
    print('Pattern: ', pattern)
    print('Match: ', match)
    print('\n')

    matches = [i.group() for i in match]
    return list(matches)

def get_search_hits(patterns, document):
    doc_name = document.split('/')[-1].replace('.pdf', '')

    start_time = datetime.now()
    print('Starting PDF conversion...')
    text = convert_pdf_to_txt(document)
    end_time = datetime.now() - start_time
    print(f'{doc_name} converted in {end_time} seconds')

    start_time = datetime.now()
    match_function = lambda x : match_pattern(text, x, doc_name)
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        match_sets = list(executor.map(match_function, patterns))
        
    match_sets = [sublist for sublist in match_sets if sublist]
    match_sets = list(set([match for sublist in match_sets for match in sublist if sublist]))
    end_time = datetime.now() - start_time
    print(f'{len(match_sets)} terms returned in {end_time} seconds:')
    print(match_sets)
    print('\n')

    return match_sets



def validate(page, term):
    pattern = f'\\b{term}\\b'
    pattern = re.compile(pattern)
    start_time = datetime.now()

    try:
        hit = page.search_for(term)
        for i in hit:
            box = page.get_textbox(i+(-10,-10,10,10))
            if re.search(pattern, box):
                continue
            hit.remove(i)


    except TypeError as e:
        print('ERROR:')
        print(term)
        print(e)
        print('\n')

    print(f'{term} on page {page} took {datetime.now() - start_time} seconds to complete')
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
            highlight = page.add_highlight_annot(hit)
            highlight.set_colors({"stroke":(0,1,0)})
            highlight.update()
        

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
    search_file = 'ema_adverse_pt.txt'
    documents_path = 'tests'
    run_highlighter(search_file, documents_path)



# if __name__ == '__main__':
#     queries = parse_queries('ema_adverse_pt.txt')
#     documents_path = '/Users/frankchlumsky/Downloads/Portugal_20220406_1_12/Native/my_highlights/Highlighted_Docs_PT'
#     document = '/Users/frankchlumsky/Downloads/Portugal_20220406_1_12/Native/my_highlights/Highlighted_Docs_PT/0009.pdf_HIGHLIGHTED.pdf'
#     get_search_hits(queries, document)


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
