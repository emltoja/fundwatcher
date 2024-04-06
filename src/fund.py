# Fund data class 
from program import FundWatcherProgram
from bs4 import BeautifulSoup
from bs4 import Tag
import json
import requests 
import datetime
import sys

CURRENT_PRICE_CLASS_NAME = "quotes_single_fund__summary-rate-number"

class FundData: 

    def __init__(self, fw_app: FundWatcherProgram, fundname: str, url: str) -> None:
        self.fw_app = fw_app
        self.fundname = fundname
        self.url = url
        self.cached_data_path = self.fw_app.get_cached_data_path()
        self.current_price = 0.0
        self._set_current_price()

    def _set_current_price_from_resp(self, resp) -> None:
        soup = BeautifulSoup(resp.content, 'html.parser')
        pricetag = soup.find("span", class_=CURRENT_PRICE_CLASS_NAME)
        if not isinstance(pricetag, Tag):
            print(f"Error: Price tag not found. {pricetag}")
            sys.exit(1)
        print(pricetag.text)
        self.current_price = float(pricetag.text.replace(',', '.').replace('\xa0', ''))

    def _set_current_price(self) -> None:
        try:
            with open(self.cached_data_path, "r", encoding='utf-8') as file:
                data = json.load(file)
                price = data[f'{self.fundname}']['price']
                if not isinstance(price, float):
                    print(f"Error: Price is not a float. It is of type {type(price)}")
                    sys.exit(1)
                self.current_price = price
        except Exception:
            print("Warning: Cache file not found. Fetching data from the website.")
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_current_price_from_resp(resp)
                self._cache_data()
            else:
                print(f"Error: Unable to connect to the website. {resp.status_code}")
                sys.exit(1)

    def _cache_data(self):
        with open(self.cached_data_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            f.seek(0)
            f.truncate(0)
            data[f'{self.fundname}'] = {
                'price': self.current_price,
                'timestamp': datetime.datetime.now().isoformat()
            }
            json.dump(data, f)

    def get_current_price(self) -> float: 
        return self.current_price
    