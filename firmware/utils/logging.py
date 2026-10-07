from typing import List

def msg_warn(*message: str):
    print("WARNING:",*message)

def msg_boot(*message: str):
    print("  [*]",message)

def msg_err(*message: str):
    print("ERROR:",*message)

__all__ = ['msg_warn','msg_boot','msg_err']