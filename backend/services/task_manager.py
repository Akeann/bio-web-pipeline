import os
import psutil
from typing import List
import signal

def get_child_processes() -> List[psutil.Process]:
    current_process = psutil.Process(os.getpid())
    return current_process.children(recursive=True)

def kill_child_processes():
    for child in get_child_processes():
        try:
            child.terminate()
        except psutil.NoSuchProcess:
            pass

def cleanup_processes():
    kill_child_processes()