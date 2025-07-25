function refreshTab(tabId) {
    fetch(`/refresh_tab/${encodeURIComponent(tabId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
}
