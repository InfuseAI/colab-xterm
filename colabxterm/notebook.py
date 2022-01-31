import html
import json
import random
import shlex

from colabxterm import manager

_CONTEXT_COLAB = "_CONTEXT_COLAB"
_CONTEXT_IPYTHON = "_CONTEXT_IPYTHON"
_CONTEXT_NONE = "_CONTEXT_NONE"


def _get_context():
    try:
        import google.colab
        import IPython
    except ImportError:
        pass
    else:
        if IPython.get_ipython() is not None:
            return _CONTEXT_COLAB

    try:
        import IPython
    except ImportError:
        pass
    else:
        ipython = IPython.get_ipython()
        if ipython is not None and ipython.has_trait("kernel"):
            return _CONTEXT_IPYTHON

    return _CONTEXT_NONE


def load_ipython_extension(ipython):
    """Register IPython line/cell magics.

    Args:
      ipython: An `InteractiveShell` instance.
    """
    ipython.register_magic_function(
        _xterm_magic,
        magic_kind="line",
        magic_name="xterm",
    )


def _xterm_magic(args_string):
    context = _get_context()
    try:
        import IPython
        import IPython.display
    except ImportError:
        IPython = None

    if context == _CONTEXT_NONE:
        handle = None
        print("Launching Xterm...")
    else:
        handle = IPython.display.display(
            IPython.display.Pretty("Launching Xterm..."),
            display_id=True,
        )

    def print_or_update(message):
        if handle is None:
            print(message)
        else:
            handle.update(IPython.display.Pretty(message))

    def is_port_in_use(port: int) -> bool:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    parsed_args = shlex.split(args_string, comments=True, posix=True)
    height = 800
    port = 10000
    while True:
        if not is_port_in_use(port):
            break
        port = port+1

    manager.start(parsed_args, port)
    fn = {
        _CONTEXT_COLAB: _display_colab,
        _CONTEXT_IPYTHON: _display_ipython,
        _CONTEXT_NONE: _display_cli,
    }[_get_context()]
    return fn(port=port, height=height)


def _display_colab(port, height):
    import IPython.display

    shell = """
        (async () => {
            const url = new URL(await google.colab.kernel.proxyPort(%PORT%, {'cache': true}));
            const iframe = document.createElement('iframe');
            iframe.src = url;
            iframe.setAttribute('width', '100%');
            iframe.setAttribute('height', '%HEIGHT%');
            iframe.setAttribute('frameborder', 0);
            document.body.appendChild(iframe);
        })();
    """
    replacements = [
        ("%PORT%", "%d" % port),
        ("%HEIGHT%", "%d" % height),
    ]
    for (k, v) in replacements:
        shell = shell.replace(k, v)
    script = IPython.display.Javascript(shell)
    IPython.display.display(script)


def _display_ipython(port, height):
    import IPython.display

    frame_id = "xterm-frame-{:08x}".format(random.getrandbits(64))
    shell = """
      <iframe id="%HTML_ID%" width="100%" height="%HEIGHT%" frameborder="0">
      </iframe>
      <script>
        (function() {
          const frame = document.getElementById(%JSON_ID%);
          const url = new URL(%URL%, window.location);
          const port = %PORT%;
          if (port) {
            url.port = port;
          }
          frame.src = url;
        })();
      </script>
    """
    replacements = [
        ("%HTML_ID%", html.escape(frame_id, quote=True)),
        ("%JSON_ID%", json.dumps(frame_id)),
        ("%HEIGHT%", "%d" % height),
        ("%PORT%", "%d" % port),
        ("%URL%", json.dumps("/")),
    ]
    for (k, v) in replacements:
        shell = shell.replace(k, v)
    iframe = IPython.display.HTML(shell)
    IPython.display.display(iframe)


def _display_cli(port, height):
    message = "Please visit http://localhost:%d in a web browser." % port
    print(message)


def list():
    infos = manager.get_all()
    if not infos:
        print("No xterm instances running.")
        return

    print("Known xterm instances:")
    for info in infos:
        template = (
            "  - port {port}: {data_source} (pid {pid})"
        )
        print(
            template.format(
                port=info.port,
                data_source=manager.data_source_from_info(info),
                pid=info.pid,
            )
        )
