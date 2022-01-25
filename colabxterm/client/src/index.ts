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
    const handleResize = () => {
        term.element.parentElement.style.height = (window.innerHeight - 16) + "px"
        fitAddon.fit();
        fetch("/resize?rows=" + term.rows + "&cols=" + term.cols)
    };

    handleResize();
    window.onresize = handleResize;

    // handle input
    const queue: string[] = [];
    const sendData = lodash.throttle(() => {
        let data = queue.join('')
        let base64str = window.btoa(data);
        fetch("/in/" + base64str);
        queue.length = 0;
    }, 100);

    term.onData((data) => {
        queue.push(data);
        sendData();
    });

    // handle output
    async function pullOutput() {
        while(true) {
            const response = await fetch("/out");
            const byteArray = new Uint8Array(await response.arrayBuffer());
            if (response) {                
                term.write(byteArray);
            }            
        }
    }
    pullOutput();
}

window.onload = main

