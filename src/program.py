import sys
import requests
import webbrowser
from bs4 import BeautifulSoup

URL = "https://www.santander.pl/tfi/fundusze-inwestycyjne"
# Get the terminal size
FUND_LINK_CLASS_NAME = "sbptfi_fund_information_table__table-details-link"
DICT_INIT_ERR_MSG = "Error: self.link_dict wasn't initialized. Run self._get_links_dict_from_resp() or self._get_links_dict_from_cache() first."
CACHE_FILE_PATH = "..\\cached_data.txt"

MYFUNDS = {
    "Santander Dłużny Krótkoterminowy",
    "Santander Obligacji Korporacyjnych", 
    "Santander Prestiż Technologii i Innowacji",
    "Santander Prestiż Dłużny Krótkoterminowy", 
    "Santander Prestiż Obligacji Korporacyjnych"    
}

class FundWatcherProgram:

    def __init__(self):

        self.url              :str  = URL
        self.cached_data_path :str  = CACHE_FILE_PATH
        self.link_dict        :dict = dict()
        self.text             :str  = ''
    

    def _set_links_dict_from_resp(self, resp: requests.Response) -> None:

        self.text = resp.text
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", class_=FUND_LINK_CLASS_NAME)
        self.link_dict = {link.text: link['href'] for link in links}


    def _set_links_dict_from_cache(self) -> None:

        try:
            with open(self.cached_data_path, "r", encoding='utf-8') as file:
                self.text = file.read()
            soup = BeautifulSoup(self.text, "html.parser")
            links = soup.find_all("a", class_=FUND_LINK_CLASS_NAME)
            self.link_dict = {link.text: link['href'] for link in links}

        except FileNotFoundError:
            print("Warning: Cache file not found. Fetching data from the website.")
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_links_dict_from_resp(resp)
                self._cache_data()
            else:
                print(f"Error: Unable to connect to the website. {resp.status_code}")
                sys.exit(1)


    def _cache_data(self) -> None:

        if not self.text:
            print(DICT_INIT_ERR_MSG)


        with open(self.cached_data_path, "w", encoding="utf-8") as file:
            file.write(self.text)


    def _open_link(self, fund_name: str) -> None :

        if len(self.link_dict) == 0:
            print(DICT_INIT_ERR_MSG)
            sys.exit(1)

        link = self.link_dict.get(fund_name)
        
        if link is None:
            print("Error: Fund not found in self.link_dict.")
            sys.exit(1)

        webbrowser.open('https://www.santander.pl' + link)


    def setup(self, use_cache=True) -> None:

        if use_cache:
            self._set_links_dict_from_cache()
        else:
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_links_dict_from_resp(resp)
            else:
                print(f"Error: Unable to connect to the website. {resp.status_code}")
                sys.exit(1)


    def get_funds_listing(self) -> list[str]:
        
        if len(self.link_dict) == 0:
            print(DICT_INIT_ERR_MSG)
            sys.exit(1)

        return list(self.link_dict.keys())
    

    def get_links_dict(self) -> dict[str, str]:

        if len(self.link_dict) == 0:
            print(DICT_INIT_ERR_MSG)
            sys.exit(1)

        return self.link_dict

    