let fuse;

// 1. ڈیٹا لوڈ کرنا
function init() {
    if (typeof searchData !== 'undefined') {
        const options = {
            keys: ['title', 'description', 'category'],
            threshold: 0.3
        };
        fuse = new Fuse(searchData, options);
    }
}

// 2. سرچ کا فنکشن (Enter Key کے لیے بھی)
document.getElementById('search-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const query = this.value;
        executeSearch(query);
    }
});

function executeSearch(query) {
    if (!query) return;
    const results = fuse.search(query);
    showResults(results.map(r => r.item));
}

// 3. ٹیب فلٹر فنکشن
function filterData(category, btn) {
    // ایکٹیو کلاس بدلنا
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    if (category === 'all') {
        showResults(searchData);
    } else {
        const filtered = searchData.filter(item => item.category === category);
        showResults(filtered);
    }
}

// 4. رزلٹ دکھانا
function showResults(items) {
    const list = document.getElementById('results');
    list.innerHTML = items.map(item => `
        <div class="card">
            <h3 style="margin:0; color:#1a0dab;">${item.title}</h3>
            <p style="color:#4d5156; font-size:14px;">${item.description}</p>
        </div>
    `).join('');
}

window.onload = init;
