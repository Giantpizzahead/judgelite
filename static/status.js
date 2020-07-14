window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);

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
                        setTimeout(runInterval, 750 + (Math.random() * 750));
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

    if (resp["error"]) {
        flavorText.innerHTML = "Uh-oh! An internal error occurred. Please notify an officer.";
        statusText.innerHTML = "Error code: " + resp["error"] + "<br>";
    }

    if (resp["verdict"]) {
        // Show flavor text
        if (resp["verdict"] == "AC") {
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
        if (resp["score"] == 0) verdictStyle = "color-red";
        else if (resp["score"] == 1) verdictStyle = "color-green";
        else verdictStyle = "color-yellow";

        // Show results
        statusText.innerHTML = `
        <h2 class="${verdictStyle}">Verdict: ${resp["verdict"]}</h2>
        Score: ${resp["score"]}<br>
        Time: ${resp["time"]}s<br>
        Memory: ${resp["memory"]} MB<br>
        Testcase: ${resp["testcase"]}<br>
        `;

        // Show debug info (if given)
        if (resp["stdout"]) {
            statusText.innerHTML += `
            <br>---DEBUG---<br>
            stdout: ${resp["stdout"]}<br>
            stderr: ${resp["stderr"]}<br>
            `;
        }
    }

    let backButton = document.createElement("input");
    backButton.setAttribute("type", "button");
    backButton.setAttribute("onclick", "location.href='/';");
    backButton.setAttribute("value", "Resubmit!");
    document.body.appendChild(backButton);
}

function displayStatus(resp) {
    // console.log("processing")
    // console.log(resp);

    statusText = document.getElementById("status-text");
    if (resp["status"]) {
        statusText.innerHTML = "Status: " + resp["status"];
    }
}