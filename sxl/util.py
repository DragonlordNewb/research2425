import sys

def tp(*args):
    # Trailoff print
    print(*args, end="")
    sys.stdout.flush()