// Function to handle Search Logic
function search() {
    const query = document.getElementById("searchBox").value.trim().toLowerCase();
    const resultsDiv = document.getElementById("results");

    // Clear previous results
    resultsDiv.innerHTML = "";

    // 1. Agar search box khali hai to message dikhayein
    if (query === "") {
        resultsDiv.innerHTML = "<p class='error-msg'>Please enter something to search...</p>";
        return;
    }

    // 2. Data filter karein (Title ya Description dono mein search hoga)
    const filtered = data.filter(item =>
        item.title.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query)
    );

    // 3. Agar koi result na milay
    if (filtered.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <p>🔍 No results found for "<strong>${query}</strong>"</p>
                <span>Try checking your spelling or use different keywords.</span>
            </div>`;
        return;
    }

    // 4. Results ko screen par dikhayein
    filtered.forEach(item => {
        const div = document.createElement("div");
        div.className = "result-item animate-up"; // Added class for animations

        div.innerHTML = `
            <h3><a href="${item.link}" target="_blank">${item.title}</a></h3>
            <p>${item.description}</p>
            <small class="link-preview">${item.link}</small>
        `;

        resultsDiv.appendChild(div);
    });
}

// 5. Bonus: Enter Key dabane par search chalanay ka tareeqa
document.getElementById("searchBox").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        search();
    }
});
