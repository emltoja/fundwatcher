from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import ScrollableContainer
from textual.screen import Screen, ModalScreen
from textual.widgets import (
     ListItem,
     ListView,
     Header,
     Footer,
     Label
)

from program import MYFUNDS

class FundItem(ListItem):
    
        def __init__(self, fund):
            super().__init__()
            self.color: str | None = None
            self.fund = fund
    
        def render(self):
            return f"[bold {('green' if self.fund in MYFUNDS else 'red') if self.color is None else self.color}]{self.fund}"
                
    
            

class FundsList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
    ]

    def __init__(self, funds):
        self.items = list(map(FundItem, funds))
        return super().__init__(*self.items, name="Lista funduszy")

    def action_select_cursor(self) -> None:
        return super().action_select_cursor()
    
    

class FundScreen(ModalScreen):

    BINDINGS = [
        ('q', 'quit', 'Quit'),
        ('d', 'toggle_dark', 'Toggle dark mode'),
        ('b', 'app.pop_screen', 'Go back')
    ]

    def __init__(self, fund, parent):
        super().__init__()
        self.fund = fund
        self.parent_app = parent 

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("https://www.santander.pl" + self.parent_app.link_dict.get(self.fund, "Brak linku do funduszu"))
        yield Footer()
            
class FundWatcherApp(App):

    CSS_PATH = "tui.tcss"

    BINDINGS = [('q', 'quit', 'Quit'), ('d', 'toggle_dark', 'Toggle dark mode')]

    def __init__(self, funds: list[str], link_dict: dict[str, str]):
        super().__init__()
        self.funds = funds
        self.link_dict = link_dict
        self.fund_list = FundsList(self.funds)
         
    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(self.fund_list)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_mount(self) -> None:
        self.fund_list.focus()

    def on_list_view_selected(self, event: FundsList.Selected) -> None: 
        if not isinstance(event.item, FundItem):
            raise ValueError("Expected FundItem")
        self.push_screen(FundScreen(event.item.fund, self))

        
    