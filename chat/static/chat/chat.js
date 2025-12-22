const ws = new WebSocket(
    `ws://${window.location.host}/ws/chat/4`
);

ws.onmessage = e => {
    const data = JSON.parse(e.data);
    document.getElementById("chat").textContent += data.token;
};

function sendMessage() {
    const input = document.getElementById("msg");
    ws.send(JSON.stringify({ message: input.value }));
    input.value = "";
}
