var wsUri = "wss://echo.websocket.org/";
var output;
var upcoming = document.getElementById("upcoming");
var complete = document.getElementById("complete");
var currentComplete = document.getElementById("currComplete");
var currentUpcoming = document.getElementById("currUpcoming")

var quoteText = "Turmoil has engulfed the Galactic Republic. The taxation of trade routes to outlying star systems is in dispute. Hoping to resolve the matter with a blockade of deadly battleships, the greedy Trade Federation has stopped all shipping to the small planet of Naboo."
var index = 0;

function init() {
    output = document.getElementById("output");
    webSocket();
}

function webSocket() {
    websocket = new WebSocket(wsUri);
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };

    getQuote();
}

function keypress(event) {
    
    // websocket.send(event.key)

    const key = event.key;
    if (key == upcoming.innerHTML[0]) {
        complete.innerHTML += key;
        upcoming.innerHTML = upcoming.innerHTML.substring(1);
        ++index;
    }
    console.log(event.key);
}

function getQuote() {
    upcoming.innerHTML = quoteText;
    complete.innerHTML = "";
}

// websocket event handler for when the websocket connection is established
function onOpen(evt) {
    writeToScreen("CONNECTED");
    doSend("WebSocket rocks");
}

// websocket event handler for when the websocket connection is closed
function onClose(evt) {
    writeToScreen("DISCONNECTED");
}

// websocket event handler for when a messaged is received from the server
function onMessage(evt) {
    writeToScreen('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
    websocket.close();
}

// websocket event handlers for errors
function onError(evt) {
    writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

function doSend(message) {
    writeToScreen("SENT: " + message);
    websocket.send(message);
}

function writeToScreen(message) {
    var pre = document.createElement("p");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = message;
    output.appendChild(pre);
}

window.addEventListener("load", init, false);
