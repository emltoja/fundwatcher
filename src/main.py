from tui import FundWatcherApp
from program import FundWatcherProgram

if __name__ == '__main__':

    prog = FundWatcherProgram()
    prog.run()

    application = FundWatcherApp(prog.get_funds_listing(), prog.get_links_dict())
    application.run()
        