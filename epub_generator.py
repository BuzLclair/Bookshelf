''' Generates the epub with the web data part and the functions from epub_utils '''

import os
import datetime
import shutil
import tqdm
from epub_utils import BOOK_PATH, create_file, read_template, create_file_bytes, \
    chapter_cleaner, get_chapter_title, str_replace, chapter_file_name, chapter_sorter
from web_studio import FetchEpubWebData, GetQuery




## Getting the book from web
book = FetchEpubWebData()
CHAPTERS = book.chapters
CHAPTERS.sort(key=chapter_sorter)


BOOK_TITLE = book.meta_data['title']
BOOK_COVER = book.meta_data['cover_url']
BOOK_AUTHOR = book.meta_data['author_name']


## SYSTEM VAR
__CONTENT_ITEM = '    <item href="text/ADD_CHAPTER" id="ADD_ID_CHAPTER" media-type="application/xhtml+xml"/>\n'
__CONTENT_REF = '    <itemref idref="ADD_ID_CHAPTER"/>\n  '
__TOC_NAV = '    <navPoint' + read_template('toc').split('<navPoint')[1].split('</navPoint>')[0] + '</navPoint>\n'




## PART 1: Architecture set-up

def architecture_setup():
    ''' set-up the epub folders architecture '''

    try:
        os.mkdir(f'{BOOK_PATH}/images')
        os.mkdir(f'{BOOK_PATH}/META-INF')
        os.mkdir(f'{BOOK_PATH}/text')
    except FileExistsError:
        pass



## PART 2: Files creation

def create_files():
    ''' creates the generic files '''

    files = dict()
    files['mimetype'] = read_template('mimetype')
    files['page_styles.css'] = read_template('page_styles')
    files['stylesheet.css'] = read_template('stylesheet')
    files['titlepage.xhtml'] = read_template('titlepage')
    files['META-INF/container.xml'] = read_template('container')
    for x in files.keys():
        create_file(f'{BOOK_PATH}/{x}', files[x])


def create_cover():
    ''' creates the cover file '''

    file_jpeg = GetQuery(BOOK_COVER).response.content
    file_path = f'{BOOK_PATH}/images/cover.jpeg'
    create_file_bytes(file_path, file_jpeg)


def create_content():
    ''' creates the content file '''

    file_txt = read_template('content')
    to_replace = ['ADD_AUTHOR', 'ADD_DATE', 'ADD_TITLE', __CONTENT_ITEM, __CONTENT_REF,'ADD_FIRST_CHAPTER']
    replacement = [BOOK_AUTHOR, datetime.datetime.utcnow().isoformat(), \
                   BOOK_TITLE, '', '', chapter_file_name(get_chapter_title(CHAPTERS[0]))]
    file_txt = str_replace(file_txt, to_replace, replacement)
    file_path = f'{BOOK_PATH}/content.txt'
    create_file(file_path, file_txt)


def create_toc():
    ''' creates the toc file '''

    file_txt = read_template('toc')
    file_txt = file_txt.replace('ADD_TITLE', BOOK_TITLE)
    file_txt = file_txt.replace(__TOC_NAV,'')
    file_path = f'{BOOK_PATH}/toc.txt'
    create_file(file_path, file_txt)


def create_chapter(chapter_html):
    ''' convert a raw html chapter into a clean html file '''

    chapter_text = chapter_cleaner(chapter_html)
    chapter_title = get_chapter_title(chapter_html)
    chapter_structure = read_template('chapter')
    chapter_clean = str_replace(chapter_structure, ['ADD_TITLE','ADD_CHAPTER'], [chapter_title,chapter_text])
    chapter_path = f'{BOOK_PATH}/text/{chapter_file_name(chapter_title)}'
    create_file(chapter_path, chapter_clean)



## PART 3: Files modif

def modif_content(content_file, chapter, nb):
    ''' modif the content file due to multi-chapters '''

    blocker = '    <item href="page_styles.css" id="page_css" media-type="text/css"/>'
    template_modified = __CONTENT_ITEM.replace('ADD_CHAPTER', chapter)
    template_modified = template_modified.replace('ADD_ID_CHAPTER', f'ch{nb}')
    content = content_file.replace(blocker, f'{template_modified}{blocker}')
    template2 = __CONTENT_REF.replace('ADD_ID_CHAPTER', f'ch{nb}')
    content = content.replace('</spine>', template2+'</spine>')
    return content


def modif_toc(toc_file, chapter, nb):
    ''' modif the toc file due to multi-chapters '''

    blocker = '</navMap>'
    toc_chunk = __TOC_NAV
    chapter_title = get_chapter_title(chapter)
    to_replace = ['ADD_CHAPTER_ID','ADD_PLAY_ORDER','ADD_CHAPTER_TITLE','ADD_CHAPTER_PATH']
    replacement = [f'ch{nb}', str(nb), chapter_title, f'text/{chapter_file_name(chapter_title)}']
    toc_chunk = str_replace(toc_chunk, to_replace, replacement)
    toc = toc_file.replace(blocker, toc_chunk+blocker)
    return toc



## PART 4: Epub final

def files_maker():
    ''' call the aforentioned functions '''

    architecture_setup()
    create_files()
    create_cover()
    create_content()
    create_toc()


def specific_files_maker():
    ''' handle the details like chapters and technical changes to generic files '''

    content_txt = open(f'{BOOK_PATH}/content.txt', 'r').read()
    toc_txt = open(f'{BOOK_PATH}/toc.txt', 'r').read()
    for nb,x in tqdm.tqdm(enumerate(CHAPTERS)):
        chapter_title = get_chapter_title(x)
        chapter_name = chapter_file_name(chapter_title)
        create_chapter(x)
        content_txt = modif_content(content_txt, chapter_name, nb+1)
        toc_txt = modif_toc(toc_txt, x, nb+1)
    create_file(f'{BOOK_PATH}/content.opf', content_txt)
    os.remove(f'{BOOK_PATH}/content.txt')
    create_file(f'{BOOK_PATH}/toc.ncx', toc_txt)
    os.remove(f'{BOOK_PATH}/toc.txt')


def epub_zip_file(file_path):
    ''' zip a given folder and convert it to epub'''

    epub_name = BOOK_TITLE
    epub_path = file_path.replace(f'/{epub_name}','')
    shutil.make_archive(epub_name, 'zip', file_path)
    os.rename(f'{os.getcwd()}/{epub_name}.zip', f'{epub_path}/{epub_name}.epub')


def make_epub():
    files_maker()
    specific_files_maker()
    epub_zip_file(BOOK_PATH)




if __name__ == '__main__':
    make_epub()
