# import os
# from parser import parse_queries
# from multiprocessing import *
# from highlighter import *

# def main():
#     search_terms = '/Users/frankchlumsky/Desktop/Desktop - MacBook Pro (2)/Work/Novartis/Tools/Portugal/Products_Portugal.txt'
#     search_terms = parse_queries(search_terms)
#     directory = '/Users/frankchlumsky/Downloads/TEST'
#     files = os.listdir(directory)
#     files = [os.path.join(directory, i) for i in files]

#     list(map(run_highlighter, files))

#     # with Pool(processes=3) as pool:
#     #     pool.map(run_highlighter, files)
#         # pool.close()
#         # pool.join()


# if __name__ == '__main__':
#     freeze_support()
#     main()