import atexit
import os
import time
import colabxterm
import argparse
from . import manager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='python -m colabxterm')
    parser.add_argument("-p", "--port", type=int, help="port number", default=10000)
    parser.add_argument("command", help="Commands to run", nargs='*')
    args = parser.parse_args()
    port = args.port
    command = args.command
    cache_key = manager.cache_key(port)
    info = manager.TensorBoardInfo(
        version='',
        start_time=int(time.time()),
        port=port,
        pid=os.getpid(),
        path_prefix='',
        logdir='',
        db='',
        cache_key=cache_key,
    )
    atexit.register(manager.remove_info_file)
    manager.write_info_file(info)    
    
    term = colabxterm.XTerm(command,port)
    term.open()
    