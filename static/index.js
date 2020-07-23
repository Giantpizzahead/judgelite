function sendData() {
    // Disable submit button while uploading data
    document.getElementById("submit-button").disabled = true;
    document.getElementById("submit-button").innerText = "Submitting...";

    // Get form data / use an AJAX request to call the submission API
    let formData = new FormData(form);
    let xhr = new XMLHttpRequest();
    xhr.onload = function() {
        let resp = JSON.parse(xhr.response);
        if (xhr.status == 200) {
            // Add job_id to URL parameters
            let refresh = window.location.protocol + "//" + window.location.host + window.location.pathname + `?job_id=${resp["job_id"]}`;
            window.history.pushState({ path: refresh }, '', refresh);
            // Display status at top of page
            let statusClone = document.getElementById("submit-status-display").content.cloneNode(true);
            document.getElementById("result-panel").innerHTML = "";
            document.getElementById("result-panel").appendChild(statusClone);
            // Smooth scroll to top of page
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else if (xhr.status == 400) {
            // Display error in a very unfriendly way
            document.getElementById("response-text").innerHTML = "Submitted form is invalid: " + resp["error"];
        }
        // Reenable submit button
        document.getElementById("submit-button").disabled = false;
        document.getElementById("submit-button").innerText = "Submit!";
    };
    xhr.open("POST", "/api/submit", true);
    xhr.send(formData);
};

// Override form's default submit behavior
const form = document.getElementById("test-form");
form.addEventListener("submit", function (event) {
    event.preventDefault();
    sendData();
});
