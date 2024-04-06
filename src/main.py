from tui import FundWatcherApp
from program import FundWatcherProgram

if __name__ == '__main__':

    prog = FundWatcherProgram()
    prog.setup()

    application = FundWatcherApp(prog)
    application.run()
        