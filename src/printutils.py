import sys

YELLOW = 93
RED = 91
CYAN = 96

def printwarning(msg: str) -> None: 

    '''
    Print a warning message to the stdout.
    '''

    print('\033[93m' + 'WARNING: ' + '\033[0m' + msg)


def printerror(msg: str) -> None: 
    
    '''
    Print an error message to the stderr.
    '''

    print('\033[91m' + 'ERROR: ' + '\033[0m' + msg, file=sys.stderr)


def printinfo(msg: str) -> None: 
        
    '''
    Print an info message to the stdout.
    '''

    print('\033[96m' + 'INFO: ' + '\033[0m' + msg)