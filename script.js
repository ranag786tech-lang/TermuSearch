/* DigiD Search - Nexus Intelligence Logic */

let fuse;

// 1. Initialize the Search Engine
function initSearch() {
    const options = {
        keys: ['title', 'description', 'tech_stack'], // Fields to search in data.js
        threshold: 0.3, // 0.0 is perfect match, 1.0 matches anything
        includeScore: true
    };

    // 'searchData' comes from your data.js file
    if (typeof searchData !== 'undefined') {
        fuse = new Fuse(searchData, options);
        console.log("DigiD Intelligence: Ready");
    } else {
        console.error("Data.js not found. Please run your crawler.py");
    }
}

// 2. Handle the Search Action
const searchInput = document.getElementById('search-input');
const resultsGrid = document.getElementById('results-grid');

searchInput.addEventListener('input', (e) => {
    const query = e.target.value;

    if (!query) {
        resultsGrid.innerHTML = ''; // Clear results if search is empty
        return;
    }

    // Use Fuse.js to find results
    const results = fuse.search(query);
    renderResults(results.map(r => r.item));
});

// 3. Render Results to the UI
function renderResults(items) {
    resultsGrid.innerHTML = items.map(item => `
        <a href="${item.url || '#'}" class="result-card" target="_blank">
            <h3>${item.title}</h3>
            <p>${item.description || 'No description available.'}</p>
            <div class="tech-tag">${item.tech_stack ? item.tech_stack.join(' • ') : 'Project'}</div>
        </a>
    `).join('');
}

// Run init on load
window.addEventListener('DOMContentLoaded', initSearch);
