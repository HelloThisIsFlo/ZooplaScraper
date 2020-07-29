import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from collections import Counter
import datetime
import matplotlib
matplotlib.use('MacOSX')


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

    def add_availability(self, date):
        def is_valid():
            today = datetime.date.today()
            num_of_days_from_today = abs((date - today).days)
            # if num_of_days_from_today > 90:
            #     return False

            # if num_of_days_from_today == 0:
            #     return False
            return True

        if is_valid():
            self.availabilities.append(date)

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
            self.add_availability(date)

        next_page_path = self._find_path_to_next_page()
        if next_page_path:
            print('Going one level deeper...')
            self.crawl(next_page_path)
        else:
            print('Done 😃')
            print()
            print()


def plot_availabilities(availabilities):
    x_axis = []
    y_axis = []
    availabilities_counter = Counter(availabilities)
    for date in availabilities_counter:
        x_axis.append(mdates.date2num(date))
        y_axis.append(availabilities_counter[date])

    plt.plot_date(x_axis, y_axis)
    plt.show()

def write_availabilities_to_csv_file(availabilities):
    filename = 'result.csv'
    availabilities_csv = [
        datetime.datetime.strftime(d, '%d/%m/%Y') for d in availabilities
    ]
    with open(filename, 'w') as csv_file:
        for availability_csv in availabilities_csv:
            csv_file.write(availability_csv)
            csv_file.write('\n')


if __name__ == "__main__":
    start_path_0mile = '/to-rent/property/london/e9/homerton-south-hackney/?beds_min=2&include_shared_accommodation=false&price_frequency=per_month&price_max=1750&price_min=1500&q=E9&radius=0&results_sort=newest_listings&search_source=refine'
    start_path_1mile = '/to-rent/property/london/e9/homerton-south-hackney/?beds_min=2&include_shared_accommodation=false&price_frequency=per_month&price_max=1750&price_min=1500&q=E9&radius=1&results_sort=newest_listings&search_source=refine'
    start_path_3mile = '/to-rent/property/london/e9/homerton-south-hackney/?beds_min=2&include_shared_accommodation=false&price_frequency=per_month&price_max=1750&price_min=1500&q=E9&radius=3&results_sort=newest_listings&search_source=refine'

    crawler = AvailabilityCrawler()
    crawler.crawl(start_path_3mile)
    # print(crawler.availabilities)
    write_availabilities_to_csv_file(crawler.availabilities)