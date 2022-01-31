import datetime
import errno
import json
import os
import subprocess
import tempfile
import time


def _get_info_file_path(pid):
    info_dir = os.path.join(tempfile.gettempdir(), ".colab-xterm-info")
    try:
        os.makedirs(info_dir)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(info_dir):
            pass
        else:
            raise
    else:
        os.chmod(info_dir, 0o777)
    return os.path.join(info_dir, f"pid-{pid}.info")


def write_info_file(pid, success, reason=None):
    data = {
        "success": success,
        "reason": reason,
    }
    payload = f"{json.dumps(data)}\n"
    print(payload)
    with open(_get_info_file_path(pid), "w") as outfile:
        outfile.write(payload)


def read_info_file(pid):
    with open(_get_info_file_path(pid), "r") as infile:
        content = infile.read()
        return json.loads(content)


def remove_info_file(pid):
    try:
        os.unlink(_get_info_file_path(pid))
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise


def start(arguments, port, timeout=datetime.timedelta(seconds=60)):
    p = subprocess.Popen(
        ["python", "-m", "colabxterm", "--port", str(port)] + arguments,
    )

    poll_interval_seconds = 0.5
    while True:
        time.sleep(poll_interval_seconds)
        subprocess_result = p.poll()
        if subprocess_result is not None:
            return
        if os.path.exists(_get_info_file_path(p.pid)):
            result = read_info_file(p.pid)
            if not result:
                return {"succes": False, "reason": "Unknown error"}
            else:
                return result
