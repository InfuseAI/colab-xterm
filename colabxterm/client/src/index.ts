import "xterm/css/xterm.css"

import { Terminal } from "xterm";
import { FitAddon } from 'xterm-addon-fit';
import lodash from 'lodash';

function main() {
    const term = new Terminal();
    const fitAddon = new FitAddon();
    (window as any).term = term;
    (window as any).fitAddon = fitAddon;
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));

    // handle resize
    const handleResize = () => {
        term.element.parentElement.style.height = (window.innerHeight - 16) + "px"
        fitAddon.fit();
        fetch("/resize?rows=" + term.rows + "&cols=" + term.cols)
    };

    handleResize();
    window.onresize = handleResize;

    // handle input
    const queue: string[] = [];
    term.onData((data) => {
        queue.push(data);
    });
    (async () => {
        const sleep = (time: number) => new Promise((resolve) => setTimeout(resolve, time))

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

