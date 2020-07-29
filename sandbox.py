from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import datetime


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


class AvailabilityCrawler:
    def __init__(self):
        self.availabilities = []
        self.base_url = 'https://www.zoopla.co.uk'
        self.html = None

    def _load_html(self, path):
        raw_html = simple_get(self.base_url + path)
        self.html = BeautifulSoup(raw_html, 'html.parser')

    def _find_path_to_next_page(self):
        for a in self.html.find_all('a'):
            if 'Next' in a.text:
                return a['href']
        return None

    def crawl(self, path):
        def extract_date_string(availability_text):
            return availability_text.split('Available')[1]\
                .replace('from', '')\
                .strip()

        def parse_date(to_parse):
            if to_parse == 'immediately':
                return datetime.date.today()
            else:
                to_parse = to_parse\
                    .replace('st', '')\
                    .replace('nd', '')\
                    .replace('rd', '')\
                    .replace('th', '')
                return datetime.datetime.strptime(to_parse, '%d %b %Y').date()

        print(f"Loading: '{path}'")
        self._load_html(path)
        for available_from in self.html.select('.available-from'):
            date_string = extract_date_string(available_from.text)
            date = parse_date(date_string)
            self.availabilities.append(date)

        next_page_path = self._find_path_to_next_page()
        if next_page_path:
            print('Going one level deeper...')
            self.crawl(next_page_path)
        else:
            print('Done 😃')
            print()
            print()


if __name__ == "__main__":
    start_path_1mile = '/to-rent/property/london/e9/homerton-south-hackney/?beds_min=2&include_shared_accommodation=false&price_frequency=per_month&price_max=1750&price_min=1500&q=E9&radius=1&results_sort=newest_listings&search_source=refine'
    start_path_0mile = '/to-rent/property/london/e9/homerton-south-hackney/?beds_min=2&include_shared_accommodation=false&price_frequency=per_month&price_max=1750&price_min=1500&q=E9&radius=0&results_sort=newest_listings&search_source=refine'

    crawler = AvailabilityCrawler()
    # crawler.crawl(start_path_0mile)

    # print(crawler.availabilities)

    availabilities = [
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 29),
        datetime.date(2020, 7, 31),
        datetime.date(2020, 8, 10),
        datetime.date(2020, 8, 15),
        datetime.date(2020, 8, 17),
        datetime.date(2020, 8, 19),
        datetime.date(2020, 8, 20),
        datetime.date(2020, 8, 21),
        datetime.date(2020, 8, 22),
        datetime.date(2020, 8, 24),
        datetime.date(2020, 8, 6),
        datetime.date(2020, 8, 8),
        datetime.date(2020, 9, 1),
        datetime.date(2020, 9, 30),
        datetime.date(2020, 9, 4),
        datetime.date(2020, 9, 7),
        datetime.date(2020, 10, 2),
        datetime.date(2020, 10, 3)
    ]

    # search_url = 'https://www.zoopla.co.uk/to-rent/property/london/e9/homerton-south-hackney/?beds_min=2&include_shared_accommodation=false&price_frequency=per_month&price_max=1750&price_min=1500&q=E9&radius=0&results_sort=newest_listings&search_source=refine'
    # raw_html = simple_get(search_url)
    # html = BeautifulSoup(raw_html, 'html.parser')
    # for available_from in html.select('.available-from'):
    #     print(available_from.text)

    # for a in html.find_all('a'):
    #     if 'Next' in a.text:
    #         print(a)
    #         print(a['href'])
