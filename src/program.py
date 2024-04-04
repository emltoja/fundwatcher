import sys
import requests
import webbrowser
from bs4 import BeautifulSoup

URL = "https://www.santander.pl/tfi/fundusze-inwestycyjne"
# Get the terminal size
FUND_LINK_CLASS_NAME = "sbptfi_fund_information_table__table-details-link"
CACHE_FILE_PATH = "..\\cached_data.txt"

MYFUNDS = {
    "Santander Dłużny Krótkoterminowy",
    "Santander Obligacji Korporacyjnych", 
    "Santander Prestiż Technologii i Innowacji",
    "Santander Prestiż Dłużny Krótkoterminowy", 
    "Santander Obligacji Skarbowych"    
}

class FundWatcherProgram:

    def __init__(self):

        self.url = URL
        self.cached_data_path = CACHE_FILE_PATH
        self.link_dict = None
        self.text = None


    

    def _get_links_dict_from_resp(self, resp: requests.Response):

        self.text = resp.text
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", class_=FUND_LINK_CLASS_NAME)
        self.link_dict = {link.text: link['href'] for link in links}


    def _get_links_dict_from_cache(self):

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
                self._get_links_dict_from_resp(resp)
                self._cache_data()
            else:
                print(f"Error: Unable to connect to the website. {resp.status_code}")
                sys.exit(1)


    def _cache_data(self):

        if isinstance(self.text, str):

            with open(self.cached_data_path, "w", encoding="utf-8") as file:
                file.write(self.text)

        else:
            print( "Error: self.text is not a string. Run self._get_links_dict_from_resp() or self._get_links_dict_from_cache() first.")

    def _open_link(self, fund_name: str):

        if self.link_dict is not None:
            link = self.link_dict.get(fund_name)
            if link is not None:
                webbrowser.open('https://www.santander.pl' + link)
            else:
                print("Error: Fund not found in self.link_dict.")
                sys.exit(1)
        else:
            print("Error: self.link_dict wasn't initialized. Run self._get_links_dict_from_resp() or self._get_links_dict_from_cache() first.")
            sys.exit(1)
    
    def run(self, use_cache=True):

        if use_cache:
            self._get_links_dict_from_cache()
        else:
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._get_links_dict_from_resp(resp)
            else:
                print(f"Error: Unable to connect to the website. {resp.status_code}")
                sys.exit(1)

    def get_funds_listing(self):
        
        funds: list[str] = []
        if isinstance(self.link_dict, dict):
            for fund in self.link_dict.keys():
                funds.append(fund)
        else:
            print("Error: self.link_dict wasn't initialized. Run self._get_links_dict_from_resp() or self._get_links_dict_from_cache() first.")
            sys.exit(1)

        return funds
    
    def get_links_dict(self):
        if not isinstance(self.link_dict, dict):
            print("Error: self.link_dict wasn't initialized. Run self._get_links_dict_from_resp() or self._get_links_dict_from_cache() first.")
            sys.exit(1)
        return self.link_dict

    