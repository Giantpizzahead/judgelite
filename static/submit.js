function toggleBonus() {
    let bonusButton = document.getElementById("bonus-button");
    let bonusContainer = document.getElementById("bonus-container");
    if (bonusContainer.style.display === "none") {
        bonusButton.innerText = "Hide Bonus";
        bonusContainer.style.display = "block";
    } else {
        bonusButton.innerText = "Show Bonus";
        bonusContainer.style.display = "none";
    }
}

function toggleHints() {
    let hintButton = document.getElementById("hint-button");
    let hintContainer = document.getElementById("hint-container");
    if (hintContainer.style.display === "none") {
        hintButton.innerText = "Hide Hints";
        hintContainer.style.display = "block";
    } else {
        hintButton.innerText = "Show Hints";
        hintContainer.style.display = "none";
    }
}

function showSubmitStatus() {
    // Display status at top of page
    let statusClone = document.getElementById("submit-status-display").content.cloneNode(true);
    document.getElementById("result-panel").innerHTML = "";
    document.getElementById("result-panel").appendChild(statusClone);
}

function sendData() {
    // Disable submit button while uploading data
    document.getElementById("submit-button").disabled = true;
    document.getElementById("submit-button").innerText = "Submitting...";

    // Get form data / use an AJAX request to call the submission API
    let formData = new FormData(submitForm);
    if (!formData.has("run_bonus")) formData.append("run_bonus", "off");
    let xhr = new XMLHttpRequest();
    xhr.onload = function() {
        document.getElementById("code").value = "";
        let resp = JSON.parse(xhr.response);
        if (xhr.status == 200) {
            // Add job_id to URL parameters
            let refresh = window.location.protocol + "//" + window.location.host + window.location.pathname + `?job_id=${resp["job_id"]}`;
            window.history.pushState({ path: refresh }, '', refresh);
            showSubmitStatus();
            // Smooth scroll to top of page
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else if (xhr.status == 400) {
            // Display error in a very unfriendly way
            document.getElementById("response-text").innerHTML = "Submission failed: " + resp["error"];
        }
        // Reenable submit button
        document.getElementById("submit-button").disabled = false;
        document.getElementById("submit-button").innerText = "Submit!";
    };
    xhr.onerror = function() {
        document.getElementById("code").value = "";
        // Display error in a very unfriendly way
        document.getElementById("response-text").innerHTML = "Error occurred while submitting. Maybe try submitting again?";
        // Reenable submit button
        document.getElementById("submit-button").disabled = false;
        document.getElementById("submit-button").innerText = "Submit!";
    }
    xhr.open("POST", "/api/submit", true);
    xhr.send(formData);
};

// Override form's default submit behavior
const submitForm = document.getElementById("submit-form");
submitForm.addEventListener("submit", function (event) {
    event.preventDefault();
    sendData();
});

window.onload = function() {
    if ((new URLSearchParams(window.location.search)).has('job_id')) {
        showSubmitStatus();
    }
};
