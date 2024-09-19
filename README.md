# colab-xterm
Colab-xterm allows you to open a terminal in a cell.

# Usage

1. Install package and load the extension
    ```
    !pip install colab-xterm
    %load_ext colabxterm
    ```
2. Open a terminal
    ```
    %xterm
    ```
3. Enjoy!

Try it out in the demo notebook. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/infuseai/colab-xterm/blob/main/demo.ipynb)

# Features
- TTY support
- Does not block your kernel

# Options

```
%xterm height=1000 port=10001
```

option | description
-------|-----------
height | The height of the terminal panel
port | The server port

# Screenshots
![](assets/colab-xterm.png)

# Star History

[![Star History Chart](https://api.star-history.com/svg?repos=InfuseAI/colab-xterm&type=Date)](https://star-history.com/#InfuseAI/colab-xterm&Date)
