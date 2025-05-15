''' Utilities module where functions used to produce the epub are defined '''

import os
import re


PROJECT_PATH = r'C:\Users\const\Documents\Code\Python\Bookshelf\Bookshelf_v3'



########## 1 - Architecture functions

def book_folder():
    ''' create the folder for the book '''

    book_path = f'{PROJECT_PATH}/Books/book_lab'
    try:
        os.mkdir(book_path)
    except FileExistsError:
        os.remove(f'{PROJECT_PATH}/Books/book_lab/')
        os.mkdir(book_path)
        # pass
    return book_path



########## 2 - Files making functions

def create_file(file_path, file_txt):
    ''' create a file given its full path and content '''

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_txt)
        file.close()


def create_file_bytes(file_path, file_bytes):
    ''' create a file given its full path and content in bytes '''

    with open(file_path, 'wb') as file:
        file.write(file_bytes)
        file.close()


def read_template(file_name):
    ''' read template of a given file ex: "mimetype" and returns the file (str) '''

    with open(f'{PROJECT_PATH}/epub_shaper/Templates/{file_name}.txt', 'r') as file:
        file_txt = file.read()
        file.close()
    return file_txt


def str_replace(string_var, to_replace, replacement):
    ''' replace the elements in a str '''

    for nb,x in enumerate(to_replace):
        string_var = string_var.replace(x, replacement[nb])
    return string_var


def str_filter(string_var, char_to_keep):
    ''' remove the elements in a str '''

    str_var = list(string_var)
    filtered_var = ''.join(list(filter(lambda x: ord(x) in char_to_keep, str_var)))
    return filtered_var


def tag_cleaner(str_var, tag1, tag2, add_tag2):
    ''' clean all between the 2 tags '''

    while str_var.find(tag1) != -1:
        index1 = str_var.find(tag1)
        index2 = str_var.find(tag2)
        str_var = str_var[:index1] + str_var[index2+add_tag2:]
    return str_var



########## 3 - Chapters related functions

## 3.1 - Generic Functions

def chapter_file_name(chapter_title):
    ''' return the name of the capter file given the html version '''

    title = chapter_title.replace(' ','_')
    char_to_keep = list(range(48,58)) + list(range(65,91))+[95]+list(range(97,123))
    title_clean = str_filter(title, char_to_keep)
    return f'{title_clean}.html'


def chapter_sorter(chapter):
    ''' returns the chapter number '''

    chap_nb = get_chapter_title(chapter).split(' ')[1].split(' ')[0]
    chap_nb_clean = ''.join(list(filter(lambda x: ord(x) in list(range(48,58)), chap_nb)))
    chap_nb_clean = chap_nb_clean.replace(':','')
    if chap_nb_clean == '':
        chap_nb = get_chapter_title(chapter).split(' ')[0].split(' ')[0]
        chap_nb_clean = ''.join(list(filter(lambda x: ord(x) in list(range(48,58)), chap_nb)))
        chap_nb_clean = chap_nb_clean.replace(':','')
    return int(chap_nb_clean)


def text_striper(text):
    ''' from html returns only the part with the chapter '''

    chapter = '<p>'.join(text.split('<p>')[1:])
    chapter_full = '</p>'.join(chapter.split('</p>')[:-1])
    return chapter_full + '</p>'


def tag_striper(text):
    ''' removes the tags other than <p> '''

    text_list = text.split('<')
    for nb,x in enumerate(text_list[:-1]):
        if x[:2] != 'p>' and x[:3] != '/p>':
            if text_list[nb].split('>')[0] == text_list[nb+1].split('>')[0][1:]:
                text_list[nb] = ''
            else:
                text_list[nb] = ''.join(x.split('>')[1:])
        else:
            text_list[nb] = '<' + text_list[nb]
    text_list[-1] = '' if text_list[-1][:3] != '/p>' else '<' + text_list[-1]
    return ''.join(text_list)


def tag_sanity(chapter):
    ''' insure that the <p> tags are closed correclty '''

    txt = chapter.replace('</p>','')
    txt_list0 = txt.split('<p>')
    txt_list = list(filter(lambda x: 'window.pub' not in x, txt_list0))
    if txt_list[1].find('</') != -1:
        chapter_clean = txt_list[0] + txt_list[1] + '<p>'
        chapter_clean += '</p><p>'.join(txt_list[2:])
    else:
        chapter_clean = txt_list[0] + '<p>'
        chapter_clean += '</p><p>'.join(txt_list[1:])
    chapter_clean += '</p>'
    return chapter_clean


def bug_striper(txt):
    ''' clean the parts with &...; '''

    perturb = list(re.finditer('&',txt))
    if not perturb:
        return txt
    indexes = [x.regs[0][0] for x in perturb]
    indexes_set = [(x,x + txt[x:x+8].find(';')) for x in indexes]
    to_remove = list(filter(lambda x: x[1] !=-1, indexes_set))
    for x in to_remove[::-1]:
        txt = txt[:x[0]] + txt[x[1]+1:]
    return txt





## 3.2 Host Specific Functions

def get_chapter_title(chapter_html):
    ''' return the title extracted from the html novel '''

    chapter_title = chapter_html.split('title="')[1].split('"')[0]
    return chapter_title


def txt_cleaner(txt):
    ''' clear str of forbidden char '''

    to_replace = ['ReadNovelFull.me?','ReadNovelFull.me','*** You are reading on https://webnovelonline.com ***',
                  'pAn,da n<0,>v,e1',"<p>The source of this content is no//vel//bi/n[.//]net' </p>",
                   "<p>The source of this content is n/ov/elb/in[./]net' </p>",
                   "<p>The source of this content is no/vel//bi/n[./]net' </p>",
                   "<p>The source of this content is n0/v//el//bin[.//]net' </p>",
                   "<p>The source of this content is n/0v//elbin[.//]net' </p>",
                   "<p>The source of this content is nov/el/b/in[./]net' </p>",
                   "<p>The source of this content is n/ov//el/bin[./]net' </p>",
                   chr(11),'&ndash;','&rsquo;','&ldquo;','&rdquo;','&prime;','&mdash;',
                   '&quot;','&#39;']
    replacement = ['***','***','***','','','','','','','','','','-',"'",'"','"',"'",'—','"',"'"]
    txt = str_replace(txt, to_replace, replacement)
    txt = bug_striper(txt)
    return txt


# '&nbsp;','&hellip;','&mdash;','&rho;','&alpha;'


def chapter_cleaner(chapter_html):
    ''' clean a raw html chapter into a clean str '''

    title = get_chapter_title(chapter_html)
    chapter = txt_cleaner(chapter_html)
    chapter = chapter.replace('<br>','<p></p>').split('</main>')[0]
    chapter = text_striper(chapter)
    chapter = tag_striper(chapter)
    chapter = tag_sanity(chapter)
    chapter_vf = f'<h3>{title}</h3>\n' + chapter.replace(title,'')
    return chapter_vf



BOOK_PATH = book_folder()
