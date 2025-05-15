import requests
import time

from requests.exceptions import ReadTimeout
from threading import Thread
from time import perf_counter
from tqdm import tqdm



class GetQuery:
    ''' Meant to perform GET requests for a given url.

    Attributes
    ----------
    _QUERY_HEADERS : dict
        Headers used for the requests queries.
    url: str
        Url on which the request should be made

    '''

    _QUERY_HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48'}


    def __init__(self, url, timeout=10):
        self.response = self.__do_query(url, timeout)


    def __do_query(self, url, timeout):
        ''' Performs the get query on the given url.

        Parameters
        ----------
        url : str
            Url used for the query.
        timeout : int
            Maximum time allocated for the requests before an exception is raised.

        Returns
        -------
        requests.models.Response
            The response of the query.

        '''

        try:
            response = requests.get(url, timeout=timeout, headers=self._QUERY_HEADERS)
            return response
        except ReadTimeout:
            print(f'The url {url} timed out.')



class FetchEpubWebData:
    ''' Meant to fetch all the novel data from the website.

    Attributes
    ----------
    None

    '''

    def __init__(self):
        self.novel_url = self.confirm_novel_url()
        self.meta_data = self.get_novel_meta_data()
        self.chapters_url = self.get_list_chapters_url()
        self.chapters = []
        self.get_all_chapters()


    def confirm_novel_url(self):
        ''' Prompt the user to give the novel Url.

        Returns
        -------
        str
            The novel Url as given by the user.

        '''

        return input('\033[1mNovel Url\033[0m: \n\n(\033[3mIt should be from the website https://novelbin.me/ and be the main page of the novel ' + \
                     'from this website where you find the novel meta data etc. \nEx: https://novelbin.me/novel-book/shadow-slave)\033[0m \n\n--> ')


    def get_novel_meta_data(self):
        ''' Get the novel meta data based on the home page info.

        Returns
        -------
        dict
            Dictionnary containing the title, cover Url and author name.

        '''

        novel_webpage = GetQuery(self.novel_url).response.text
        title = novel_webpage.split('<h3 class="title">')[1].split('</')[0]
        cover = novel_webpage.split('<h2>Novel info</h2>')[1].split('<img')[1].split('src="')[1].split('"')[0]
        author = novel_webpage.split('<h3>Author:</h3>')[1].split('>')[1].split('<')[0]
        return {'title':title, 'cover_url':cover, 'author_name':author}


    def get_list_chapters_url(self):
        ''' Returns a list with all the chapters Url.

        Returns
        -------
        list_chapters_url: list
            List all the available chapters Url.

        '''

        novel_id = self.novel_url.split('/')[-1]
        chapters_lst_root_url = 'https://novelbin.com/ajax/chapter-archive?novelId='
        chapters_lst_url = f'{chapters_lst_root_url}{novel_id}'
        list_chapters_url_html = GetQuery(chapters_lst_url).response.text
        list_chapters_url_raw = list_chapters_url_html.split('<li>')[1:]
        list_chapters_url = [text.split('</li>')[0].split('href="')[1].split('"')[0] for text in list_chapters_url_raw]
        return list_chapters_url


    def get_chapter_text(self, chapter_url):
        ''' Get chapter Url as input and returns the chapter text.

        Parameters
        ----------
        chapter_url : str
            The Url of the chqpter.

        '''

        chapter_page = GetQuery(chapter_url).response.text
        chapter_txt = '<h2>' + chapter_page.split('<h2>')[1].split('<p style="display')[0]
        self.chapters.append(chapter_txt)


    def get_all_chapters(self):
        ''' Get all chapters with multithreading.

        Returns
        -------
        threads : list
            All the chapters in html format.

        '''

        start = perf_counter()
        threads = []
        for url in tqdm(self.chapters_url):
            time.sleep(2.0)
            t = Thread(target = self.get_chapter_text, args=(url,))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        print(f'{len(self.chapters_url)} chapters fetched in {(perf_counter()-start):.2f}s')
        return threads






# https://novelbin.com/b/shadow-slave
# z = FetchEpubWebData()
