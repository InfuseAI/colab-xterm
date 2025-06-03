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

    # Defaults
    height = 800
    port = 10000
    font_size = 14
    font_family = "monospace"
    command = None

    parsed_args = shlex.split(args_string, comments=True, posix=True)

    # Parse arguments
    user_args = []
    for parameter in parsed_args:
        kv_pair = str(parameter).split('=', 1)
        if len(kv_pair) == 2:
            k, v = kv_pair
            if k == "height" and v.isdigit():
                height = int(v)
            elif k == "port" and v.isdigit():
                port = int(v)
            elif k == "fontsize" and v.isdigit():
                font_size = int(v)
            elif k == "fontfamily":
                font_family = v
            elif k == "command":
                command = v
            else:
                user_args.append(parameter)
        else:
            user_args.append(parameter)
    # Clean parsed_args as an empty list to avoid the disability of the magic line command.
    parsed_args = []

    # Find available port
    while True:
        if not is_port_in_use(port):
            break
        port += 1

    # Pass command to manager if needed
    # If 'command' is specified, put it as the first argument to manager.start
    manager_args = []
    if command:
        manager_args = [command]
    manager.start(manager_args, port)

    # Build query parameters for the frontend
    query_params = [
        f"fontsize={font_size}",
        f"fontfamily={html.escape(font_family)}"
    ]
    if command:
        query_params.append(f"command={html.escape(command)}")
    query_string = "&".join(query_params)

    fn = {
        _CONTEXT_COLAB: lambda **kwargs: _display_colab(query_string=query_string, **kwargs),
        _CONTEXT_IPYTHON: lambda **kwargs: _display_ipython(query_string=query_string, **kwargs),
        _CONTEXT_NONE: lambda **kwargs: _display_cli(**kwargs),
    }[_get_context()]
    return fn(port=port, height=height)


def _display_colab(port, height, query_string=""):
    import IPython.display

    shell = f"""
        (async () => {{
            const url = new URL(await google.colab.kernel.proxyPort({port}, {{'cache': true}}));
            url.search = "{'?' + query_string if query_string else ''}";
            const iframe = document.createElement('iframe');
            iframe.src = url;
            iframe.setAttribute('width', '100%');
            iframe.setAttribute('height', '{height}');
            iframe.setAttribute('frameborder', 0);
            document.body.appendChild(iframe);
        }})();
    """
    script = IPython.display.Javascript(shell)
    IPython.display.display(script)


def _display_ipython(port, height, query_string=""):
    import IPython.display

    frame_id = "xterm-frame-{:08x}".format(random.getrandbits(64))
    shell = f"""
      <iframe id="{html.escape(frame_id, quote=True)}" width="100%" height="{height}" frameborder="0"></iframe>
      <script>
        (function() {{
          const frame = document.getElementById({json.dumps(frame_id)});
          const url = new URL({json.dumps("/")}, window.location);
          const port = {port};
          if (port) {{
            url.port = port;
          }}
          url.search = "{'?' + query_string if query_string else ''}";
          frame.src = url;
        }})();
      </script>
    """
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