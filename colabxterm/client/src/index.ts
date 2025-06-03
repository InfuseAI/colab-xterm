import "xterm/css/xterm.css"

import { Terminal } from "xterm";
import { FitAddon } from 'xterm-addon-fit';
import lodash from 'lodash';

// Utility to parse query params from the URL
function getQueryParam(key: string): string | null {
    const params = new URLSearchParams(window.location.search);
    return params.get(key);
}

function main() {
    const fontFamily = getQueryParam('fontfamily') || 'monospace';
    const fontSizeRaw = getQueryParam('fontsize');
    const fontSize = fontSizeRaw && !isNaN(Number(fontSizeRaw))
        ? parseInt(fontSizeRaw, 10)
        : 14;

    // If you want to use a command parameter, retrieve it as well:
    const command = getQueryParam('command'); // Not used directly here, backend executes it

    const term = new Terminal({
        fontFamily,
        fontSize
    });
    const fitAddon = new FitAddon();

    (window as any).term = term;
    (window as any).fitAddon = fitAddon;
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));

    // handle resize
    const handleResize = () => {
        if (term.element && term.element.parentElement) {
            term.element.parentElement.style.height = (window.innerHeight - 16) + "px";
        }
        fitAddon.fit();
        fetch("/resize?rows=" + term.rows + "&cols=" + term.cols);
    };

    handleResize();
    window.onresize = handleResize;

    // handle input
    const queue: string[] = [];
    term.onData((data) => {
        queue.push(data);
    });
    (async () => {
        const sleep = (time: number) => new Promise((resolve) => setTimeout(resolve, time));
        try {
            while (true) {
                await sleep(100);
                if (!lodash.isEmpty(queue)) {
                    let data = queue.join('');
                    let base64str = window.btoa(data);
                    queue.length = 0;
                    await fetch("/in/" + base64str);
                }
            }
        } finally {
            console.log("input disconnect!");
        }
    })();

    // handle output
    async function pullOutput() {
        try {
            while (true) {
                const response = await fetch("/out");
                const byteArray = new Uint8Array(await response.arrayBuffer());
                if (response) {
                    term.write(byteArray);
                }
            }
        } finally {
            console.log("input disconnect!");
        }
    }
    pullOutput();
}

window.onload = main