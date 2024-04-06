import sys
import requests
import webbrowser
import datetime
import json
from bs4 import BeautifulSoup

URL = "https://www.santander.pl/tfi/fundusze-inwestycyjne"
FUND_LINK_CLASS_NAME = "sbptfi_fund_information_table__table-details-link"
DICT_INIT_ERR_MSG = "Error: self.link_dict wasn't initialized. Run self._get_links_dict_from_resp() or self._get_links_dict_from_cache() first."
CACHE_FILE_PATH = ".\\cached_data.json"

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

        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", class_=FUND_LINK_CLASS_NAME)
        self.link_dict = {link.text: link['href'] for link in links}


    def _set_links_dict_from_cache(self) -> None:

        try:
            with open(self.cached_data_path, "r", encoding='utf-8') as file:
                data = json.load(file)['FundList']
                self.link_dict = data['links']

        except FileNotFoundError:
            print("Warning: Cache file not found. Fetching data from the website.")
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_links_dict_from_resp(resp)
                self._cache_data()
            else:
                print(f"Error: Unable to connect to the website. {resp.status_code}")
                sys.exit(1)


    def _cache_data(self, file=None) -> None:

        if len(self.link_dict) == 0:
            print(DICT_INIT_ERR_MSG)

        data = {
            'FundList': {
                'links': self.link_dict,
                'timestamp': datetime.datetime.now().isoformat()
            }
        }

        if file is None:
            with open(self.cached_data_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        else: 
            json.dump(data, file)


    def _open_link(self, fund_name: str) -> None :

        if len(self.link_dict) == 0:
            print(DICT_INIT_ERR_MSG)
            sys.exit(1)

        link = self.link_dict.get(fund_name)
        
        if link is None:
            print("Error: Fund not found in self.link_dict.")
            sys.exit(1)

        webbrowser.open('https://www.santander.pl' + link)


    def setup(self) -> None:

        try: 
            with open(self.cached_data_path, "r", encoding='utf-8') as file:
                data = json.load(file)['FundList']
                timestamp = data['timestamp']
                if datetime.datetime.fromisoformat(timestamp) < datetime.datetime.now() - datetime.timedelta(days=7):
                    resp = requests.get(self.url, timeout=5)
                    if resp.status_code == 200:
                        self._set_links_dict_from_resp(resp)
                        self._cache_data(file)
                    else:
                        print(f"Error: Unable to connect to the website. {resp.status_code}")
                        sys.exit(1)
                else:
                    self._set_links_dict_from_cache()
            
        except FileNotFoundError:
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_links_dict_from_resp(resp)
                self._cache_data()
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
    
    def get_cached_data_path(self) -> str:
        return self.cached_data_path

    