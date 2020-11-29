var wsUri = "ws://localhost:6789";
var upcoming = document.getElementById("upcoming");
var complete = document.getElementById("complete");
var currentComplete = document.getElementById("currComplete");
var currentUpcoming = document.getElementById("currUpcoming")
var gameNumber = document.getElementById("gameNumber");
var gamesList = document.getElementById("gamesList");
var playersDiv = document.getElementById("players");
var typingbox = document.getElementById("typingbox");

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
    const key = event.key;
    if (key == upcoming.innerHTML[0]) {
        complete.innerHTML += key;
        upcoming.innerHTML = upcoming.innerHTML.substring(1);
        ++index;
    }
    // websocket.send(event.key)
    // Expect: {"type": "update", "game_ID": "", "player_ID":"", "word_num": 0}
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

var currentGame;
var myPlayerID;
function onJoinGame(msg) {
    typingbox.setAttribute("disabled","disabled");
    typingbox.value = "";
    upcoming.innerHTML = msg.paragraph;
    complete.innerHTML = "";
    playersDiv.innerHTML = "";
    currentGame = msg.game_ID;
    myPlayerID = msg.player_ID;
    const heading = document.createElement("h3");
    heading.innerHTML = "Game " + currentGame + ". You are Player " + myPlayerID;
    playersDiv.append(heading);
    const readyButton = document.createElement("button");
    readyButton.setAttribute("onclick", "readyup()")
    readyButton.innerHTML = "Click when ready";
    playersDiv.append(readyButton);
    msg.all_player_IDs.forEach(player => {
        const p = document.createElement("div");
        p.setAttribute("class", "player");
        const sp = document.createElement("span");
        if (player == myPlayerID) {
            sp.innerHTML = "Player " + player + " (YOU)";
        } else {
            sp.innerHTML = "Player " + player;
        }
        p.append(sp);
        playersDiv.append(p);
    });

}

function readyup() {
    msg = {"type": "player_status", "game_ID": currentGame, "player_ID": myPlayerID, "status": "ready"}
    websocket.send(JSON.stringify(msg));
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

async function onGameStatus(msg) {
    var cntdown = document.createElement("h3");
    playersDiv.append(cntdown);
    if (msg.status == "countdown") {
        var t = msg.time_length_seconds;
        while (t > 0) {
            cntdown.innerHTML = t--;
            await sleep(1000);
        }
        cntdown.innerHTML = "GO";
    }
    else if (msg.status == "started") {
        typingbox.removeAttribute("disabled");
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
        case "game_status":
            onGameStatus(msg);
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

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

window.addEventListener("load", init, false);
