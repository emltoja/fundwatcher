'''
Fund data class
'''

import sys
import json
import datetime
import requests
from bs4 import Tag
from bs4 import BeautifulSoup
from printutils import *
from program import FundWatcherProgram

CURRENT_PRICE_CLASS_NAME = "quotes_single_fund__summary-rate-number"


class FundData:
    '''
    Class representing data about a single fund
    '''

    def __init__(self, fw_app: FundWatcherProgram, fundname: str, url: str) -> None:

        self.fw_app = fw_app
        self.fundname = fundname
        self.url = url
        self.cached_data_path = self.fw_app.get_cached_data_path()
        self.current_price = 0.0
        self.graph = []
        self._set_current_price_from_cache()
        # self._set_graph_from_cache()

    def _set_current_price_from_resp(self, resp: requests.Response) -> None:

        soup = BeautifulSoup(resp.content, 'html.parser')
        pricetag = soup.find("span", class_=CURRENT_PRICE_CLASS_NAME)
        if not isinstance(pricetag, Tag):
            print(f"Error: Price tag not found. {pricetag}")
            sys.exit(1)
        print(pricetag.text)
        self.current_price = float(
            pricetag.text.replace(',', '.').replace('\xa0', ''))

    def _set_graph_from_resp(self, resp: requests.Response) -> None:

        soup = BeautifulSoup(resp.content, 'html.parser')
        path = soup.find("g")
        if not isinstance(path, Tag):
            printerror(f"Graph tag not found. {path}")
            sys.exit(1)
        data = path['d']
        if not isinstance(data, str):
            printerror(
                f"Graph data is not a string. It is of type {type(data)}")
            sys.exit(1)
        self.graph = data.split(' ')

    def _set_graph_from_cache(self) -> None:
        try:
            with open(self.cached_data_path, "r", encoding='utf-8') as file:
                data = json.load(file)
                graph = data[f'{self.fundname}']['graph']
                if not isinstance(graph, list):
                    printerror(
                        f"Graph is not a list. It is of type {type(graph)}")
                    sys.exit(1)
                self.graph = graph

        except FileNotFoundError:
            printerror(
                "Cache file not found. Please run FundWatcherProgram.setup() first.")
            sys.exit(1)

        except KeyError:
            printwarning(
                f"Graph for {self.fundname} not found. Fetching data from the website.")
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_graph_from_resp(resp)
                self._cache_data()
            else:
                printerror(
                    f"Unable to connect to the website. {resp.status_code}")
                sys.exit(1)

    def _set_current_price_from_cache(self) -> None:

        try:
            with open(self.cached_data_path, "r", encoding='utf-8') as file:
                data = json.load(file)
                timestamp = data[f'{self.fundname}']['timestamp']

                if datetime.datetime.now() - datetime.datetime.fromisoformat(timestamp) > datetime.timedelta(hours=1):
                    printwarning(
                        "Cache file is outdated. Fetching data from the website.")
                    resp = requests.get(self.url, timeout=5)
                    if resp.status_code == 200:
                        self._set_current_price_from_resp(resp)
                        self._cache_data()
                    else:
                        printerror(
                            f"Unable to connect to the website. {resp.status_code}")
                        sys.exit(1)

                else:
                    price = data[f'{self.fundname}']['price']
                    if not isinstance(price, float):
                        printerror(
                            f"Price is not a float. It is of type {type(price)}")
                        sys.exit(1)
                    self.current_price = price

        except FileNotFoundError:
            printerror(
                "Cache file not found. Please run FundWatcherProgram.setup() first.")
            sys.exit(1)

        except KeyError:

            printwarning(
                f"Price for {self.fundname} not found. Fetching data from the website.")
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self._set_current_price_from_resp(resp)
                self._cache_data()
            else:
                printerror(
                    f"Unable to connect to the website. {resp.status_code}")
                sys.exit(1)

    def _cache_data(self) -> None:

        with open(self.cached_data_path, "r+", encoding="utf-8") as file:
            data = json.load(file)
            file.seek(0)
            file.truncate(0)
            data[f'{self.fundname}'] = {
                'price': self.current_price,
                'timestamp': datetime.datetime.now().isoformat()
            }
            json.dump(data, file)

    # ====== GETTERS =======

    def get_fw_app(self) -> FundWatcherProgram:
        return self.fw_app

    def get_cached_data_path(self) -> str:
        return self.cached_data_path

    def get_current_price(self) -> float:
        return self.current_price

    def get_graph(self) -> list:
        return self.graph

    def get_fundname(self) -> str:
        return self.fundname

    def get_url(self) -> str:
        return self.url
