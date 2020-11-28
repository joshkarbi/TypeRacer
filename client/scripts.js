var wsUri = "ws://localhost:6789";
var upcoming = document.getElementById("upcoming");
var complete = document.getElementById("complete");
var currentComplete = document.getElementById("currComplete");
var currentUpcoming = document.getElementById("currUpcoming")

var quoteText = "Turmoil has engulfed the Galactic Republic. The taxation of trade routes to outlying star systems is in dispute. Hoping to resolve the matter with a blockade of deadly battleships, the greedy Trade Federation has stopped all shipping to the small planet of Naboo."
var index = 0;

function init() {
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
}

function newGame() {
    msg = {"type": "new_game"}
    websocket.send(JSON.stringify(msg));
}

function onNewGame(msg) {
    console.log(msg);
}

function joinGame(id) {
    msg = {"type": "join_game", "game_id": id}
    websocket.send(JSON.stringify(msg))
}

function onJoinGame(msg) {
    console.log(msg);
}

function getQuote() {
    upcoming.innerHTML = quoteText;
    complete.innerHTML = "";
}


function onMessage(evt) {
    const msg = JSON.parse(evt.data);
    switch(msg.type) {
        case "connected":
            console.log('Websocket connection successful');
            break;
        case "games":
            showGames(msg);
            break;
        case "new_game":
            onNewGame(msg);
            break;
        case "join_game":
            onJoinGame(msg);
            break;
    }
}

// websocket event handler for when the websocket connection is established
function onOpen(evt) {
    console.log(evt)
}

// websocket event handler for when the websocket connection is closed
function onClose(evt) {
    console.log(evt);
}

// websocket event handlers for errors
function onError(evt) {
    console.log(evt.data);
}

window.addEventListener("load", init, false);
