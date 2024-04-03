import os

# Get the terminal size
rows, columns = os.popen('stty size', 'r').read().split()

# Print "FUNDWATCHER" centered according to the terminal size
print("FUNDWATCHER".center(int(columns), "="))