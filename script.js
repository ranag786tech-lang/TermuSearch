// ============================================
// یہ تمہارا موجودہ کوڈ ہے (جیسے کا ویسے رہنے دو)
// ============================================

let selectedTab = 'All';

function setTab(element, tabName) {
    selectedTab = tabName;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    element.classList.add('active');
    search();
}
async function search(query) {
    const url = `https://api.duckduckgo.com/?q=${query}&format=json&pretty=1`;
    const response = await fetch(url);
    const data = await response.json();
    
    // DuckDuckGo se related topics dikhao
    const results = data.RelatedTopics;
    displayResults(results);
}
 if (query === "") {
        resultsDiv.innerHTML = "<p style='color: #666;'>Search box khali hai. Kuch type karein...</p>";
        return;
    }

    const filtered = data.filter(item => {
        const matchesQuery = item.title.toLowerCase().includes(query) || 
                             item.description.toLowerCase().includes(query) ||
                             (item.keywords && item.keywords.some(k => k.toLowerCase().includes(query)));
        const matchesTab = (selectedTab === 'All') || (item.category === selectedTab);
        return matchesQuery && matchesTab;
    });

    if (filtered.length === 0) {
        resultsDiv.innerHTML = `<div class="no-results"><p>🔍 "<strong>${query}</strong>" ke mutabiq kuch nahi mila.</p></div>`;
        return;
    }

    filtered.forEach(item => {
        const div = document.createElement("div");
        div.className = "result-item";
        div.innerHTML = `
            <h3><a href="${item.link}" target="_blank">${item.title}</a></h3>
            <span class="category-tag">${item.category || 'General'}</span>
            <p>${item.description}</p>
            <small>${item.link}</small>
        `;
        resultsDiv.appendChild(div);
    });
// Enter key support
document.getElementById("searchBox").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        search();
    }
});

// ============================================
// 🆕 یہ نئی چیز شامل کرو (اختیاری)
// ============================================

// یہ فنکشن بتائے گا کہ کتنے results ملے
function showResultCount() {
    const query = document.getElementById("searchBox").value.toLowerCase();
    const count = data.filter(item => 
        item.title.toLowerCase().includes(query) || 
        item.description.toLowerCase().includes(query)
    ).length;
    
    const countDiv = document.getElementById("resultCount");
    if (countDiv) {
        countDiv.innerHTML = `About ${count} results`;
    }
}

// جب بھی search ہو، count بھی دکھائے
const originalSearch = search;
window.search = function() {
    originalSearch();
    showResultCount();
};
