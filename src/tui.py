import webbrowser 
from program import FundWatcherProgram
from fund import FundData
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

from program import MYFUNDS

class FundItem(ListItem):
    
        def __init__(self, fund: str):
            super().__init__()
            self.color: str | None = None
            self.fund = fund
    
        def render(self) -> str:
            return f"[bold {('green' if self.fund in MYFUNDS else 'red') if self.color is None else self.color}]{self.fund}"
                
    
            

class FundsList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
    ]

    def __init__(self, funds: list[str]):
        self.items = list(map(FundItem, funds))
        return super().__init__(*self.items, name="Lista funduszy")

    def action_select_cursor(self) -> None:
        return super().action_select_cursor()
    
    
class FundWatcherApp(App):

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
        self.pricelist = self._get_price_list()

    def _get_price_list(self) -> dict[str, float]:
        return {fund: FundData(self.fw_prog, fund, "https://www.santander.pl" + self.link_dict.get(fund, "")).get_current_price() for fund in self.funds}
         
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

    BINDINGS: list[BindingType] = [
        Binding('q', 'quit', 'Quit'),
        Binding('d', 'toggle_dark', 'Toggle dark mode'),
        Binding('escape,b', 'app.pop_screen', 'Go back')
    ]

    def __init__(self, fund: str, parent: FundWatcherApp):
        super().__init__()
        self.fund = fund
        self.parent_app = parent 
        self.link = "https://www.santander.pl" + self.parent_app.link_dict.get(self.fund, "") if self.fund in self.parent_app.link_dict else ''
        self.fundprice = self.parent_app.pricelist.get(self.fund, -1.0)

    def on_mount(self) -> None:
        self.title = self.fund
        self.sub_title = "Hyperlink to the fund"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(self.link)
        yield LinkButton(self.link)
        yield Label(f"Current price: {self.fundprice}")
        yield Footer()

class LinkButton(Button):

    def __init__(self, link: str):
        self.link = link
        return super().__init__("Open link")
    
    
    def on_click(self):
        webbrowser.open(self.link)
    
            

        
    