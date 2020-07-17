const urlParams = new URLSearchParams(window.location.search);
const QUERY_DELAY = 750;
window.onload = function() {
    // Repeatedly query for status
    if (urlParams.has("job_id")) {
        runInterval();
    }
}

var xhttp;
var xmlHttpTimeout;
var numFailed = 1;
function runInterval() {
    xmlHttpTimeout = setTimeout(handleRequestError, 5000);
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE) {
            clearTimeout(xmlHttpTimeout);
            if (this.status == 200) {
                displayResults(JSON.parse(xhttp.responseText));
            } else if (this.status == 202) {
                displayStatus(JSON.parse(xhttp.responseText));
                // Random timeout to make it exciting! (and to spread out server request load)
                setTimeout(runInterval, QUERY_DELAY + (Math.random() * QUERY_DELAY));
            } else {
                // Unexpected result; treat as an error
                handleRequestError();
            }
        }
    }
    xhttp.open("GET", "/results/" + urlParams.get("job_id"), true);
    xhttp.send();
}

function handleRequestError() {
    xhttp.abort();
    statusText = document.getElementById("status-text");
    if (numFailed > 5) {
        statusText.innerHTML = "Status: Error contacting server. Maybe try reloading the page?";
        return;
    } else {
        statusText.innerHTML = "Status: Error contacting server. Retrying... [Try #" + numFailed + "]";
    }
    numFailed++;
    setTimeout(runInterval, numFailed * QUERY_DELAY);
}

function displayResults(resp) {
    // console.log("finished")
    // console.log(resp);

    flavorText = document.getElementById("flavor-text");
    statusText = document.getElementById("status-text");
    rawText = document.getElementById("raw-text");
    rawText.innerText = JSON.stringify(resp);

    if ("error" in resp) {
        flavorText.innerHTML = "Uh-oh! An internal error occurred. If the issue persists, please notify an officer.";
        statusText.innerHTML = "=====DEBUG INFO=====<br>Error code: " + resp["error"] + "<br>Job ID: " + resp["job_id"];
    } else if ("verdict" in resp && resp["verdict"] == "CE") {
        flavorText.innerHTML = "Were you tooooooo fast?";
        statusText.innerHTML = `
        <h2 class="color-red">Verdict: ${resp["verdict"]}</h2>
        Score: ${resp["score"]}/${resp["max_score"]}<br>
        `;
        debugText = statusText.appendChild(document.createElement("p"));
        debugText.className = "color-red";
        debugText.innerText = `=====ERROR LOG=====
        ${resp["compile_error"]}`;
    } else if ("verdict" in resp) {
        // Show flavor text
        if (resp["verdict"] == "AC*") {
            flavorText.innerHTML = "Whoa! What an overachiever :P [Really though, nice job. That was impressive.]"
        } else if (resp["verdict"] == "AC") {
            flavorText.innerHTML = "Congrats! I knew you could do it :D";
        } else if (resp["verdict"] == "WA") {
            flavorText.innerHTML = "Proof by AC? More like proof by WA :P";
        } else if (resp["verdict"] == "TLE") {
            flavorText.innerHTML = "Aww what? I thought for sure that time complexity would work! :(";
        } else if (resp["verdict"] == "MLE") {
            flavorText.innerHTML = "Yikes. I hope you know how to do sliding window!";
        } else if (resp["verdict"] == "RE") {
            flavorText.innerHTML = "Oh no... Not a runtime error! Good luck debugging THAT one.";
        }

        // Set verdict color based on score
        let verdictStyle;
        if (resp["score"] > resp["max_score"]) verdictStyle = "color-blue";
        else if (resp["score"] == resp["max_score"]) verdictStyle = "color-green";
        else if (resp["score"] > 0) verdictStyle = "color-yellow";
        else verdictStyle = "color-red"

        // Show results
        statusText.innerHTML = `
        <h2 class="${verdictStyle}">Verdict: ${resp["verdict"]}</h2>
        Score: ${resp["score"]}/${resp["max_score"]}<br>
        Time: ${resp["time"]}ms<br>
        Memory: ${resp["memory"]} MB<br>
        Testcase: ${resp["testcase"]}<br>
        `;

        // Show debug info (if given)
        if ("stdout" in resp) {
            debugText = statusText.appendChild(document.createElement("p"));
            debugText.innerText = `=====DEBUG=====
            -----stdout-----
            ${resp["stdout"]}
            -----stderr-----
            ${resp["stderr"]}
            `;
        }
    } else {
        flavorText.innerHTML = "Uh-oh! An internal error occurred. If the issue persists, please notify an officer.";
        statusText.innerHTML = "=====DEBUG INFO=====<br>Error code: EMPTY_RESULT<br>Job ID: " + resp["job_id"];
    }

    let backButton = document.createElement("button");
    backButton.setAttribute("onclick", "window.history.back();");
    backButton.innerText = "Go Back";
    document.body.appendChild(backButton);
}

function displayStatus(resp) {
    // console.log("processing")
    // console.log(resp);

    statusText = document.getElementById("status-text");
    if ("status" in resp) {
        statusText.innerHTML = "Status: " + resp["status"];
    }

    rawText = document.getElementById("raw-text");
    rawText.innerText = JSON.stringify(resp);
}
