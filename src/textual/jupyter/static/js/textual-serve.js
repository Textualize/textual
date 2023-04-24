
class TextualTerminal {
    constructor(element) {
        const self = this;
        console.log(element.dataset);
        this.element = element;
        this.websocket_url  = element.dataset.sessionWebsocketUrl;
        console.log("websocket_url", this.websocket_url)
        this.terminal = new Terminal({
          allowProposedApi: true,
          fontSize: 16,
          // disableLigatures: true,
          // customGlyphs: true,
          fontFamily: "Menlo, Monaco, 'Courier New', monospace"
        });

        this.fitAddon = new FitAddon.FitAddon();
        this.terminal.loadAddon(this.fitAddon);
        this.webglAddon = new WebglAddon.WebglAddon();
        this.terminal.loadAddon(this.webglAddon);
        // this.canvasAddon = new CanvasAddon.CanvasAddon()
        // this.terminal.loadAddon(this.canvasAddon);
        // this.unicode11Addon = new Unicode11Addon.Unicode11Addon();
        // this.terminal.loadAddon(this.unicode11Addon);
        this.terminal.open(element);
        this.socket = null;

        this.bufferedBytes = 0;
        this.refreshBytes = 0;
        this.size = null;

        this.terminal.onResize((event) => {
          console.log("RESIZE");
          self.size = {"width": event.cols, "height": event.rows}
          self.sendSize();
        });

        this.terminal.onData((data) => {
          this.socket.send(JSON.stringify(["stdin", data]));
        })

        window.onresize = () => {
          this.fit()
        }

        setInterval(() => {
          console.log(self.bufferedBytes);
        }, 1000.)
    }

    sendSize() {
      const self = this;
      if (self.size){
        const meta = JSON.stringify([
          "resize",
          self.size
        ]);
        if (this.socket){
          this.socket.send(meta);
        }
      }
    }

    fit() {
      const self = this;
      self.fitAddon.fit(self.element);
    }

    connect() {
        console.log("SERVE")
        const self = this;
        this.socket = new WebSocket(this.websocket_url);
        this.socket.binaryType = "arraybuffer";

        // Connection opened
        this.socket.addEventListener("open", (event) => {
          console.log("WS opened")
          // socket.send("Hello Server!");
          self.element.classList.add("-connected");
          self.fit();
          self.sendSize();
        });

        // Listen for messages
        this.socket.addEventListener("message", (event) => {
          console.log(event);
          var bytearray = new Uint8Array( event.data );
          self.bufferedBytes += bytearray.length;
          self.refreshBytes += bytearray.length;
          this.terminal.write(bytearray, () => {
            self.bufferedBytes -= bytearray.length;
          });
          console.log("message", bytearray.length);
          if (self.refreshBytes > 50000) {
            self.terminal.clearTextureAtlas();
            self.refreshBytes = 0;
          }

        });

    }


}

// window.onload = (event) => {
//   alert("LOAD")
//   const terminals = document.querySelectorAll(".textual-terminal");
//   terminals.forEach((terminal_element)=>{
//     textual_terminal = new TextualTerminal(terminal_element);
//     textual_terminal.fit();
//     textual_terminal.connect()
//   });
// }
