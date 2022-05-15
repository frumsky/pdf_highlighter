#!/usr/bin/env python
# -*- coding: utf-8 -*-
from parser import parse_queries
from text_extractor import convert_pdf_to_txt
import os
import fitz
from tqdm import tqdm
import time
import csv
from datetime import datetime
import re2 as re
from pathlib import Path
from pdfminer.pdfparser import PDFSyntaxError
from multiprocessing import Pool
from concurrent import futures
import sys


search_file = '/Users/frankchlumsky/Projects/Coding/Highlighter/ema_adverse.txt'
documents_path = '/Users/frankchlumsky/Downloads/Saudi_20220511_31/Native'
sys.stdout = open(f'{documents_path}/highlight_log.txt', 'w')

def match_pattern(text, pattern, doc_name):
    match = re.finditer(pattern, text)
    match = list(match)
    if not match:
        return
    # print('\n')
    # print('Document: ', doc_name)
    # print('Pattern: ', pattern)
    # print('Match: ', match)
    # print('\n')

    matches = [i.group() for i in match]
    return list(matches)

def convert_to_txt(document):
    doc = fitz.open(document)
    pages = [doc[i] for i in range(0, doc.page_count)]
    get_page_text = lambda page : page.get_text().encode("utf8")
    text_pages = list(map(get_page_text, pages))
    text_pages = [i.decode('utf-8') for i in text_pages]

    return ' '.join(text_pages)


# convert_to_txt('/Users/frankchlumsky/Projects/Coding/Highlighter/tests/0021.pdf_HIGHLIGHTED.pdf')


def get_search_hits(patterns, document):
    doc_name = document.split('/')[-1].replace('.pdf', '')

    start_time = datetime.now()
    print('Starting PDF conversion...')
    print('\n')
    text = convert_to_txt(document)
    end_time = datetime.now() - start_time
    print(f'{doc_name} converted in {end_time} seconds')
    print('\n')

    start_time = datetime.now()
    match_function = lambda x : match_pattern(text, x, doc_name)
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        match_sets = list(executor.map(match_function, patterns))
        
    match_sets = [sublist for sublist in match_sets if sublist]
    match_sets = list(set([match for sublist in match_sets for match in sublist if sublist]))
    end_time = datetime.now() - start_time
    print(f'{doc_name}: {len(match_sets)} terms returned in {end_time} seconds:')
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

    # print(f'{term} on page {page} took {datetime.now() - start_time} seconds to complete')
    return hit

def highlight_hits(terms, document):
    path = f"{'/'.join(document.split('/')[0:-1])}/Highlighted"
    doc_name = document.split('/')[-1].replace('.pdf', '')

    start_time = datetime.now()

    highlighted = False
    doc = fitz.open(document)
    pages = [doc[i] for i in range(0, doc.page_count)]
    
    # with open(f'{path}/highlight_report.csv', 'a+', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    
    if not os.path.exists(path):
        os.mkdir(path)
    f = open(f'{path}/highlight_report.csv', 'a+', encoding='utf-8')
    writer = csv.writer(f)
    if os.path.getsize(f'{path}/highlight_report.csv') == 0:
        writer.writerow(['Document', 'Page', 'Highlight'])

    for page in pages:
        page_no = str(page).split(' ')[1]
        start_time = datetime.now()
        find_hits = lambda x : validate(page, x)
        hits = list(map(find_hits, terms))


        start_time = datetime.now()
        for hit in hits:
            if not hit:
                continue
            writer.writerow([doc_name, page_no, [page.get_textbox(box) for box in hit]])
            highlighted = True
            highlight = page.add_highlight_annot(hit)
            highlight.set_colors({"stroke":(0,1,0)})
            highlight.update()

    print(f'{doc_name}: It took {datetime.now() - start_time} to validate and highlight hits on {len(pages)} pages\n')
        

    if highlighted:
        doc.save("%s/%s.pdf"% (path, doc_name), garbage=4, deflate=True, clean=True, ascii=True)

    f.close()

def wrapper(tup):
    query_file = tup[0]
    document = tup[1]
    doc_name = document.split('/')[-1].replace('.pdf', '')

    start = datetime.now()
    queries = parse_queries(query_file)


    try:
        search_terms = get_search_hits(queries, document)
        highlight_hits(search_terms, document)
    except (UnboundLocalError, PDFSyntaxError) as e:
        pass
    print(f'{doc_name}: The entire process took {datetime.now() - start} second\n')

def run_highlighter(st_path, dir):
    files = os.listdir(dir)
    files = [(st_path, os.path.join(dir, i)) for i in files]
    
    with Pool(processes=3) as pool:
        pool.imap_unordered(wrapper, files)
        pool.close()
        pool.join()

if __name__ == '__main__':

    run_highlighter(search_file, documents_path)
    sys.stdout.close()



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
