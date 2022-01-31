import colabxterm
import argparse
import colabxterm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='python -m colabxterm')
    parser.add_argument("-p", "--port", type=int,
                        help="port number", default=10000)
    parser.add_argument("command", help="Commands to run", nargs='*')
    args = parser.parse_args()
    port = args.port
    command = args.command
    term = colabxterm.XTerm(command, port)
    term.open()
