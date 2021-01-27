import re
from create_html import wikipedia_html



reference1 = {'title': 'Kirn, Walter (11 June 2000).',
             'link_title': "\"Happy Families Are Not All Alike\"",
             'link_url': 'https://movies2.nytimes.com/books/00/06/11/reviews/000611.11kirngt.html'}

reference2 = {'title': 'Maslin, Janet (8 June 2000).',
             'link_title': "\"BOOKS OF THE TIMES; Wising Up, Though He Ain't No Bigger Than a Poot (Published 2000)\"",
             'link_url': 'https://www.nytimes.com/2000/06/08/books/books-of-the-times-wising-up-though-he-ain-t-no-bigger-than-a-poot.html'}

reference3 = {'title': 'Optics, Hecht, 4th edition, pp. 386-7'}

content = {'title': 'Jim the Boy',
           'url': 'Jim_the_Boy',
           'content': 'Jim the Boy is a coming-of-age novel by Tony Earley, published by Little, Brown in 2000. It details the early life of Jim Glass, who lives with his mother, Elizabeth, and three uncles, in the small fictional town of Aliceville, North Carolina.',
           'references': [reference1, reference2, reference3],
           'languages': ['Deutsch', 'עברית', '中文'],
           'categories': ['2000 American novels', 'Novels set in North Carolina', 'Little, Brown and Company books', 'American bildungsromans', '2000s young adult novel stubs', 'Bildungsroman stubs']}


def main():
    html = wikipedia_html(content)
    html_file = open('altgoogle/wiki/html_test.html', "w")
    html_file.write(html)
    html_file.close()


if __name__ == "__main__":
    main()