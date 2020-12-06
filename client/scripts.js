var wsUri = document.documentURI.indexOf("TypeRacer")>0 ? "ws://localhost:6789" : "ws://18.215.229.34:6789";
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
    websocket.onopen = function(evt) { 
        onOpen(evt);
        const urlParams = new URLSearchParams(window.location.search);
        console.log("Joining game", urlParams.get("game_id"));
        if (urlParams.get("game_id") != null) {
            sleep(10);
            joinGame(null, provided_id=urlParams.get("game_id"));
        }
    };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };

    
}

let wrongKeys = [];
let wordNum = 0;
function keypress(event) {
    const key = event.key;
    if (key == upcoming.innerHTML[0] && wrongKeys.length == 0) {
        complete.innerHTML += key;
        upcoming.innerHTML = upcoming.innerHTML.substring(1);
        ++index;
        if (key == ' ') {
            typingbox.value = "";
        }
        if (upcoming.innerHTML[0] == ' ' || upcoming.innerHTML.length == 0) {
            msg = {"type": "update", "game_ID": currentGame, "player_ID": myPlayerID, "word_num": ++wordNum};
            websocket.send(JSON.stringify(msg));
        }
    }
    else if (key == 'Backspace') {
        wrongKeys.pop(key);
    }
    else if (key != 'Shift' && key != 'Alt' && key != 'Tab' && key != 'CapsLock' && key != 'Enter') {
        wrongKeys.push(key);
    }
}

function newGame() {
    msg = {"type": "new_game"}
    websocket.send(JSON.stringify(msg));
}

function onNewGame(msg) {
    console.log(msg);
    sleep(500);
    joinGame(null, msg.game_ID);
}

function joinGame(id, provided_id=null) {
    msg = {"type": "join_game", "game_ID": provided_id==null ? gameNumber.value : provided_id}
    websocket.send(JSON.stringify(msg))
}

var currentGame;
var myPlayerID;
function onJoinGame(msg) {
    if (currentGame == null || currentGame != msg.game_ID) {
        myPlayerID = msg.player_ID;
        currentGame = msg.game_ID;
    }

    typingbox.setAttribute("disabled","disabled");
    typingbox.value = "";
    upcoming.innerHTML = msg.paragraph;
    complete.innerHTML = "";
    playersDiv.innerHTML = "";
    const heading = document.createElement("h3");
    heading.innerHTML = "Game " + currentGame + ". You are Player " + myPlayerID;
    playersDiv.append(heading);

    const link = document.createElement("h4");
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("game_id") != null) {
            var shareable_link = document.documentURI;
    } else {
        var shareable_link = document.documentURI + "?game_id=" + currentGame;
    }
    link.innerHTML = "Joinable game link: " + shareable_link;
    link.id = "shareable_link"
    playersDiv.append(link);

    const readyButton = document.createElement("button");
    readyButton.setAttribute("onclick", "readyup()")
    readyButton.innerHTML = "Click when ready";
    playersDiv.append(readyButton);

    document.querySelector("#enterGameArea").hidden = true;

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
        const progress = document.createElement("span");
        progress.setAttribute("id", "progress" + player)
        progress.innerHTML = "Progress: 0 %";
        p.append(progress);

        const carDiv = document.createElement("div");
        carDiv.setAttribute("class", "carDiv");
        p.append(carDiv);

        const car = document.createElement("img");
        car.setAttribute("src", "images/cars/car" + player % 4 + ".PNG");
        car.setAttribute("class", "cars");
        car.setAttribute("id", "car" + player);
        carDiv.append(car);

    });


}

function onUpdate(msg) {
    if (currentGame == msg.game_ID) {
        if (msg.status == 'in_progress') {
            msg.updates.forEach(update => {
                let prog = document.getElementById("progress" + update.player_ID);
                prog.innerHTML = "Progress: " + update.progress + " %";
                let car = document.getElementById("car" + update.player_ID);
                car.setAttribute("style", "left: " + (update.progress / 100) * 600 + "px");
            })
        }
        else if (msg.status == 'finished') {
            let prog = document.getElementById("progress" + msg.winner_ID);
            prog.innerHTML = "Progress: 100 %";
            let car = document.getElementById("car" + msg.winner_ID);
            car.setAttribute("style", "left: 600px");
            let gameStatus = document.getElementById("gamestatus");
            let announcement = "Player " + msg.winner_ID + " is the winner!";
            gameStatus.innerHTML = announcement.fontcolor("blue");
        }
    }
}

function readyup() {
    msg = {"type": "player_status", "game_ID": currentGame, "player_ID": myPlayerID, "status": "ready"}
    websocket.send(JSON.stringify(msg));
}

function getGames() {
    msg = {"type": "get_games"}
    websocket.send(JSON.stringify(msg))
}

function quitGame() {
    msg = {"type":"disconnect"}
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
    const cntdown = document.createElement("h3");
    cntdown.setAttribute("id","gamestatus");
    playersDiv.append(cntdown);
    if (msg.status == "countdown") {
        wrongKeys = [];
        wordNum = 0;
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
        case "update":
            onUpdate(msg);
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
