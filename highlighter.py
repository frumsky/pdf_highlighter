#!/usr/bin/env python
# -*- coding: utf-8 -*-
from parser import parse_queries
import os
import fitz

import time
import csv
from datetime import datetime
import re
from pathlib import Path
from pdfminer.pdfparser import PDFSyntaxError
from multiprocessing import Pool, freeze_support
from concurrent import futures
import sys


class Highlight_Set:
    def __init__(self, txt_doc, color):
        self.queries = parse_queries(txt_doc)
        self.color = color

class Highlighter:
    def __init__(self, sets, path):
        self.sets = sets
        self.path = path
        self.files = os.listdir(path)
        self.files = [os.path.join(path, i) for i in self.files]

    def match_pattern(self, text, pattern):
        match = re.finditer(pattern, text)
        match = list(match)
        if not match:
            return

        matches = [i.group() for i in match]
        return list(matches)

    def convert_to_txt(self, document):
        doc = fitz.open(document)
        pages = [doc[i] for i in range(0, doc.page_count)]
        get_page_text = lambda page : page.get_text().encode("utf8")
        text_pages = list(map(get_page_text, pages))
        text_pages = [i.decode('utf-8') for i in text_pages]

        return ' '.join(text_pages)


    def get_search_hits(self, highlight_set, text):
        # doc_name = document.split('/')[-1].replace('.pdf', '')

        # start_time = datetime.now()
        # print('Starting PDF conversion...')
        # print('\n')
        # end_time = datetime.now() - start_time
        # print(f'{doc_name} converted in {end_time} seconds')
        # print('\n')

        start_time = datetime.now()
        match_function = lambda x : self.match_pattern(text, x)
        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            match_sets = list(executor.map(match_function, highlight_set.queries))

        # print(match_sets)
            
        match_sets = [sublist for sublist in match_sets if sublist]
        match_sets = list(set([match for sublist in match_sets for match in sublist if sublist]))
        match_sets = [(match, highlight_set.color) for match in match_sets]
        end_time = datetime.now() - start_time
        # print(f'{doc_name}: {len(match_sets)} terms returned in {end_time} seconds:')
        # print(match_sets)
        # print('\n')

        return match_sets


    def validate(self, page, term):

        search_term = term[0]
        pattern = f'\\b{search_term}\\b'
        pattern = re.compile(pattern)
        start_time = datetime.now()

        try:
            hit = page.search_for(search_term)
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

        return (hit, term[1])


    def highlight_hits(self, terms, document):
        terms = [term for sublist in terms for term in sublist if sublist]

        path = f"{'/'.join(document.split('/')[0:-1])}/Highlighted"
        doc_name = document.split('/')[-1].replace('.pdf', '')

        start_time = datetime.now()

        highlighted = False
        doc = fitz.open(document)
        pages = [doc[i] for i in range(0, doc.page_count)]
        
        
        if not os.path.exists(path):
            os.mkdir(path)
        f = open(f'{path}/highlight_report.csv', 'a+', encoding='utf-8')
        writer = csv.writer(f)
        if os.path.getsize(f'{path}/highlight_report.csv') == 0:
            writer.writerow(['Document', 'Page', 'Highlight'])

        for page in pages:
            page_no = str(page).split(' ')[1]
            start_time = datetime.now()
            find_hits = lambda x : self.validate(page, x)
            hits = list(map(find_hits, terms))

            start_time = datetime.now()
            for hit, color in hits:
                if not hit:
                    continue
                writer.writerow([doc_name, page_no, [page.get_textbox(box) for box in hit]])
                highlighted = True
                highlight = page.add_highlight_annot(hit)
                if color == 'Green':
                    highlight.set_colors({"stroke":(0,1,0)})
                    highlight.update()
                elif color == 'Yellow':
                    highlight.set_colors({"stroke":(1,1,0)})
                    highlight.update()

        print(f'{doc_name}: It took {datetime.now() - start_time} to validate and highlight hits on {len(pages)} pages\n')
            

        if highlighted:
            doc.save("%s/%s.pdf"% (path, doc_name), garbage=4, deflate=True, clean=True, ascii=True)

        f.close()


    def wrapper(self, file):
        doc_name = file.split('/')[-1].replace('.pdf', '')
        start = datetime.now()

        try:
            doc_text = self.convert_to_txt(file)
        except fitz.fitz.FileDataError as e:
            return

        try:
            get_search_terms = lambda x : self.get_search_hits(x, doc_text)
            search_terms = list(map(get_search_terms, self.sets))
            self.highlight_hits(search_terms, file)
        except (UnboundLocalError, PDFSyntaxError) as e:
            pass
        print(f'{doc_name}: The entire process took {datetime.now() - start} second\n')


    def run_highlighter(self):
        with Pool(processes=3) as pool:
            list(pool.imap_unordered(self.wrapper, self.files))
            pool.close()
            pool.join()


if __name__ == '__main__':
    freeze_support()
    highlight_fields = [
        Highlight_Set('ema_adverse_pt.txt', 'Yellow'),
        Highlight_Set('test_hits.txt', 'Green')
    ]

    highlighter = Highlighter(highlight_fields, 'test_folder')
    highlighter.run_highlighter()
    


