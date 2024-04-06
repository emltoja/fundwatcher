'''
Text User Interface for FundWatcher
'''

import webbrowser
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import (
     ListItem,
     ListView,
     Header,
     Footer,
     Label,
     Button
)
from program import FundWatcherProgram, MYFUNDS
from fund import FundData

class FundItem(ListItem):

    '''
    Fund record in the FundsList
    '''

    def __init__(self, fund: str):
        super().__init__()
        self.color: str = ''
        self.fund = fund

    def render(self) -> str:
        fund_color = 'green' if self.fund in MYFUNDS else 'red'
        return f"[bold {fund_color if not self.color else self.color}] {self.fund} [/]"




class FundsList(ListView):

    '''
    List of funds
    '''

    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
    ]

    def __init__(self, funds: list[str]):
        self.items = list(map(FundItem, funds))
        super().__init__(*self.items, name="Lista funduszy")


class FundWatcherApp(App):

    '''
    Main application class
    '''

    CSS_PATH = "tui.tcss"

    BINDINGS: list[BindingType] = [
        Binding('q', 'quit', 'Quit'),
        Binding('d', 'toggle_dark', 'Toggle dark mode')
    ]

    def __init__(self, fw_prog: FundWatcherProgram):
        super().__init__()
        self.fw_prog = fw_prog
        self.funds = fw_prog.get_funds_listing()
        self.link_dict = fw_prog.get_links_dict()
        self.fund_list = FundsList(self.funds)
        self.pricelist = self._get_price_dict()

    def _construct_link(self, fund_name: str) -> str:
        return "https://www.santander.pl" + self.link_dict.get(fund_name, "")

    def _get_price_dict(self) -> dict[str, float]:
        return {
            fund: FundData(self.fw_prog, fund, self._construct_link(fund)).get_current_price()
                for fund in self.funds
        }

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="FUNDWATCHER")
        yield ScrollableContainer(self.fund_list)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_mount(self) -> None:
        self.title = "FundWatcher"
        self.sub_title = "Santander Investment Funds"
        self.fund_list.focus()

    def on_list_view_selected(self, event: FundsList.Selected) -> None:
        if not isinstance(event.item, FundItem):
            raise ValueError("Expected FundItem")
        self.push_screen(FundScreen(event.item.fund, self))

class FundScreen(ModalScreen):

    '''
    Scrren shown after selecting a fund
    '''

    BINDINGS: list[BindingType] = [
        Binding('q', 'quit', 'Quit'),
        Binding('d', 'toggle_dark', 'Toggle dark mode'),
        Binding('escape,b', 'app.pop_screen', 'Go back')
    ]

    def __init__(self, fund: str, parent: FundWatcherApp):
        super().__init__()
        self.fund = fund
        self.parent_app = parent
        self.link = self.parent_app._construct_link(self.fund)
        self.fundprice = self.parent_app.pricelist.get(self.fund, -1.0)

    def on_mount(self) -> None:
        self.title = self.fund
        self.sub_title = "Hyperlink to the fund"

    def compose(self) -> ComposeResult:
        yield Header()
        yield LinkButton(self.link)
        yield Label(f"Current price: {self.fundprice}")
        yield Footer()

class LinkButton(Button):

    '''
    Button to open the link in the browser
    '''
    def __init__(self, link: str):
        self.link = link
        super().__init__("Open link")


    def on_click(self):
        webbrowser.open(self.link)
