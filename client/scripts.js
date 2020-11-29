var wsUri = "ws://localhost:6789";
var upcoming = document.getElementById("upcoming");
var complete = document.getElementById("complete");
var currentComplete = document.getElementById("currComplete");
var currentUpcoming = document.getElementById("currUpcoming")
var gameNumber = document.getElementById("gameNumber");
var gamesList = document.getElementById("gamesList");
var playersDiv = document.getElementById("players");

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
    msg = {"type": "join_game", "game_ID": gameNumber.value}
    websocket.send(JSON.stringify(msg))
}

function onJoinGame(msg) {
    upcoming.innerHTML = msg.paragraph;
    complete.innerHTML = "";
    playersDiv.innerHTML = "";
    const heading = document.createElement("h3").innerHTML = "Game " + msg.game_ID + ". Get Ready!";
    playersDiv.append(heading);
    msg.player_IDs.forEach(player => {
        const p = document.createElement("div");
        p.setAttribute("class", "player");
        const sp = document.createElement("span").innerHTML = "Player " + player;
        p.append(sp);
        playersDiv.append(p);
    });

}

function getGames() {
    msg = {"type": "get_games"}
    websocket.send(JSON.stringify(msg))
}

function showGames(msg) {
    let games = "";
    msg.games.forEach(g => {
        games += g + ", ";
    })
    if (games.length == 0) {
        gamesList.innerHTML = "No games found"
    } else {
        gamesList.innerHTML = games;
    }
}

function onMessage(evt) {
    const msg = JSON.parse(evt.data);
    switch(msg.type) {
        case "connected":
            console.log('Websocket connection successful');
            break;
        case "get_games":
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
