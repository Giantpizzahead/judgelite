const urlParams = new URLSearchParams(window.location.search);
const QUERY_DELAY = 1000;
window.onload = function() {
    // Repeatedly query for status
    if (urlParams.has("job_id")) {
        setTimeout(runInterval, 750);
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
                updateResults(JSON.parse(xhttp.responseText));
                finalizeResults(JSON.parse(xhttp.responseText));
            } else if (this.status == 202) {
                let shortWait = updateResults(JSON.parse(xhttp.responseText));
                // Random timeout to make it exciting! (and to spread out server request load)
                if (shortWait) {
                    setTimeout(runInterval, QUERY_DELAY + (Math.random() * QUERY_DELAY));
                } else {
                    // Wait longer (currently in queue)
                    setTimeout(runInterval, QUERY_DELAY * 4 + (Math.random() * QUERY_DELAY));
                }
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
    let statusText = document.getElementById("status-text");
    if (numFailed > 5) {
        statusText.innerHTML = "Error contacting server. Please try again in a bit.";
        return;
    } else {
        statusText.innerHTML = "Error contacting server. Retrying... [Try #" + numFailed + "]";
    }
    numFailed++;
    setTimeout(runInterval, numFailed * QUERY_DELAY);
}

function displayTestResult(verdict, subtask, test, time=0, memory=0) {
    let testResultsBox = document.querySelector("#test-results-box");
    let template = document.querySelector("#test-result");

    // Clone & fill in the template
    let clone = template.content.cloneNode(true);
    let tooltip = clone.querySelector(".tooltip-no-underline");
    let testResult = clone.querySelector(".test-result");
    let testVerdict = clone.querySelector(".test-verdict");
    let testNumber = clone.querySelector(".test-number");
    let testMemory = clone.querySelector(".test-memory");
    let testTime = clone.querySelector(".test-time");

    if (subtask != 0) testNumber.innerText = subtask + "-" + test;
    else testNumber.innerText = test;

    if (verdict == "AC" || verdict == "BO") {
        tooltip.setAttribute("title", "Correct answer");
        testResult.classList.add(verdict == "AC" ? "test-result-pass" : "test-result-bonus");
        testVerdict.innerText = "*";
        testMemory.innerText = memory + "mb";
        testTime.innerText = time + "ms";
    } else if (verdict == "SK") {
        tooltip.setAttribute("title", "Test skipped");
        testResult.classList.add("test-result-fail");
        testVerdict.innerText = "-";
    } else {
        testResult.classList.add("test-result-fail");
        if (verdict == "WA") {
            tooltip.setAttribute("title", "Wrong answer");
            testVerdict.innerText = "x";
        } else if (verdict == "TLE") {
            tooltip.setAttribute("title", "Time limit exceeded");
            testVerdict.innerText = "t";
        } else {
            tooltip.setAttribute("title", "Runtime error or memory limit exceeded");
            testVerdict.innerText = "!";
        }
    }

    // Add the clone to the page
    testResultsBox.appendChild(clone);
}

function updateResults(resp) {
    // Debug info
    // let rawText = document.getElementById("raw-text");
    // rawText.innerText = JSON.stringify(resp);

    // Clear test results
    document.querySelector("#test-results-box").innerHTML = "";

    // Update status text
    let statusText = document.getElementById("status-text");
    if (resp["status"] == "queued") {
        statusText.innerHTML = "Waiting...";
        return false;
    } else if (resp["status"] == "judging") {
        statusText.innerHTML = "Judging in progress...";
    } else if (resp["status"] == "done") {
        statusText.innerHTML = "Judging complete! Score: " + resp["final_score"] + " out of " + resp["max_score"];
    } else if (resp["status"] == "compile_error") {
        statusText.innerHTML = "Compilation error :(";
        document.querySelector("#submission-result-box").classList.add("test-result-fail");
        document.querySelector("#test-results-box").innerText = resp["compile_error"];
        return true;
    }

    // Show test results
    let testsTotal = 0;
    let testsCompleted = 0;
    let printSubtasks = true;
    if (resp["subtasks"].length == 1 || (resp["subtasks"].length == 2 && resp["is_bonus"][0] == 0 && resp["is_bonus"][1] == 1)) {
        // Special case: Make the test output prettier by removing subtask numbers
        printSubtasks = false;
    }
    for (let i = 0; i < resp["subtasks"].length; i++) {
        let subtask = resp["subtasks"][i];
        let subtaskNum = i+1;
        for (let j = 0; j < subtask.length; j++) {
            let test = subtask[j];
            if (test[0] != '--') {
                testsCompleted++;
                if (resp["is_bonus"][i] == 1 && test[0] == 'AC') {
                    displayTestResult('BO', printSubtasks ? i+1 : 0, printSubtasks ? j+1 : testsTotal+j+1, test[1], test[2].toFixed(1));
                } else if (resp["is_bonus"][i] == 0) {
                    displayTestResult(test[0], printSubtasks ? i+1 : 0, printSubtasks ? j+1 : testsTotal+j+1, test[1], test[2].toFixed(1));
                }
            }
        }
        testsTotal += subtask.length;
    }

    let progressPercent = Math.round(testsCompleted / testsTotal * 100);
    if (resp["status"] == "judging") {
        statusText.innerHTML = `Judging in progress (${progressPercent}%)...`
    }
    return true;
}

function finalizeResults(resp) {
    let backButton = document.createElement("button");
    backButton.setAttribute("onclick", "window.history.back();");
    backButton.innerText = "Go Back";
    document.body.appendChild(backButton);
}
