var urlParams = new URLSearchParams(window.location.search);
var QUERY_DELAY = 1000;
// Repeatedly query for status
if (urlParams.has("job_id")) {
    runInterval();
}

var xhr;
var xmlHttpTimeout;
var numDelay = 0;
var numFailed = 1;
function runInterval() {
    xmlHttpTimeout = setTimeout(handleRequestError, 5000);
    xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE) {
            clearTimeout(xmlHttpTimeout);
            if (this.status == 200) {
                let noError = updateResults(JSON.parse(xhr.response));
                finalizeResults(JSON.parse(xhr.responseText), noError);
            } else if (this.status == 202) {
                let shortWait = updateResults(JSON.parse(xhr.response));
                // Random timeout to make it exciting! (and to spread out server request load)
                if (shortWait) {
                    setTimeout(runInterval, QUERY_DELAY + (Math.random() * QUERY_DELAY));
                } else {
                    // Wait longer (currently in queue)
                    numDelay++;
                    setTimeout(runInterval, QUERY_DELAY * numDelay + (Math.random() * QUERY_DELAY));
                }
            } else {
                // Unexpected result; treat as an error
                handleRequestError();
            }
        }
    }
    xhr.open("GET", "/api/get_status/" + urlParams.get("job_id"), true);
    xhr.send();
}

function handleRequestError() {
    xhr.abort();
    let statusText = document.querySelector("#submission-result-box .status-text");
    if (numFailed > 3) {
        statusText.innerHTML = "Error contacting server. Please try again in a bit.";
        return;
    } else {
        statusText.innerHTML = "Error contacting server. Retrying... [Try #" + numFailed + "]";
    }
    numFailed++;
    setTimeout(runInterval, numFailed * 2 * QUERY_DELAY);
}

function displayTestResult(verdict, subtask, test, isBonus, time=0, memory=0) {
    let testResultsBox = document.querySelector("#submission-result-box .test-results-box");
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

    if (verdict == "AC") {
        tooltip.setAttribute("title", "Correct answer");
        testResult.classList.add(isBonus ? "test-result-bonus" : "test-result-pass");
        testVerdict.innerText = "*";
        testMemory.innerText = memory + "mb";
        testTime.innerText = time + "ms";
    } else if (verdict == "SK") {
        tooltip.setAttribute("title", "Test skipped");
        testResult.classList.add(isBonus ? "test-result-skipped" : "test-result-fail");
        testVerdict.innerText = "-";
    } else {
        testResult.classList.add(isBonus ? "test-result-skipped" : "test-result-fail");
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
    document.querySelector("#submission-result-box .test-results-box").innerHTML = "";

    // Update status text
    let statusText = document.querySelector("#submission-result-box .status-text");
    if (resp["status"] == "queued") {
        statusText.innerHTML = "Waiting...";
        return false;
    } else if (resp["status"] == "judging") {
        statusText.innerHTML = "Grading in progress";
    } else if (resp["status"] == "done") {
        statusText.innerHTML = "Grading complete! Score: " + resp["final_score"] + " / " + resp["max_score"];
    } else if (resp["status"] == "compile_error") {
        statusText.innerHTML = "Compilation error :(";
        document.querySelector("#submission-result-box").classList.add("submission-result-compile-error");
        document.querySelector("#submission-result-box .test-results-box").innerText = resp["error"];
        return false;
    } else if (resp["status"] == "internal_error") {
        statusText.innerHTML = "Uh-oh! An internal error occured. :(";
        document.querySelector("#submission-result-box").classList.add("submission-result-compile-error");
        document.querySelector("#submission-result-box .test-results-box").innerText = "Error code: " + resp["error"];
        return false;
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
        let subtaskIsBonus = resp["is_bonus"][i] == 1;
        let atLeast1AC = false;
        for (let j = 0; j < subtask.length; j++) {
            let test = subtask[j]
            if (test[0] == "AC") {
                atLeast1AC = true;
                break;
            }
        }
        for (let j = 0; j < subtask.length; j++) {
            let test = subtask[j];
            if (test[0] != "--") {
                testsCompleted++;
                if (!subtaskIsBonus || atLeast1AC) {
                    displayTestResult(test[0], printSubtasks ? i+1 : 0, printSubtasks ? j+1 : testsTotal+j+1, subtaskIsBonus, test[1], test[2].toFixed(1));
                }
            }
        }
        testsTotal += subtask.length;
    }

    // Update progress indicator
    let progressPercent = Math.round(testsCompleted / testsTotal * 100);
    document.querySelector("#submission-result-box .progress-box").style.width = `${progressPercent}%`;

    return true;
}

function finalizeResults(resp, noError) {
    let progressBox = document.querySelector("#submission-result-box .progress-box");

    // Color progress indicator based on results
    if (noError) {
        if (resp["final_score"] <= 0) {
            progressBox.classList.add("progress-box-fail");
        } else if (resp["final_score"] < resp["max_score"]) {
            progressBox.classList.add("progress-box-partial");
        } else {
            progressBox.classList.add("progress-box-pass");
        }
    }

    // Remove loader
    document.querySelector("#submission-result-box .loader").remove();

    // Create back button
    // let backButton = document.createElement("button");
    // backButton.setAttribute("onclick", "window.history.back();");
    // backButton.innerText = "Go Back";
    // document.body.appendChild(backButton);
}
