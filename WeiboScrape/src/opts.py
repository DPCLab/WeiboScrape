import sys

def is_local():
    return "--local" in sys.argv

def is_debug():
    return "--debug" in sys.argv

def show_head():
    return "--head" in sys.argv