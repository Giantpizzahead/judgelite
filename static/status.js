window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const QUERY_DELAY = 750

    // Repeatedly query for status
    if (urlParams.has("job_id")) {
        function runInterval() {
            let xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status == 200) {
                        displayResults(JSON.parse(xhttp.responseText));
                    } else if (this.status == 202) {
                        displayStatus(JSON.parse(xhttp.responseText));
                        // Random timeout to make it exciting! (and to spread out server request load)
                        setTimeout(runInterval, QUERY_DELAY + (Math.random() * QUERY_DELAY));
                    }
                }
            }
            xhttp.open("GET", "/results/" + urlParams.get("job_id"), true);
            xhttp.send();
        }
        runInterval();
    }
}

function displayResults(resp) {
    // console.log("finished")
    // console.log(resp);

    flavorText = document.getElementById("flavor-text");
    statusText = document.getElementById("status-text");

    if ("error" in resp) {
        flavorText.innerHTML = "Uh-oh! An internal error occurred. If the issue persists, please notify an officer.";
        statusText.innerHTML = "=====DEBUG INFO=====<br>Error code: " + resp["error"] + "<br>Job ID: " + resp["job_id"];
    }

    if ("verdict" in resp) {
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
        } else if (resp["verdict"] == "CE") {
            flavorText.innerHTML = "Were you tooooooo fast?";
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
        Time: ${resp["time"]}s<br>
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
}
