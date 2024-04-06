'''
Entry point.
'''

from program import FundWatcherProgram
from tui import FundWatcherApp

if __name__ == '__main__':

    prog = FundWatcherProgram()
    prog.setup()

    application = FundWatcherApp(prog)
    application.run()
        