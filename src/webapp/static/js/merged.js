// Category rules
function addCategoryRule() {
    const category = document.getElementById("input-category")
    const regex = document.getElementById("input-regex")
    const tbody = document.getElementById("edit-category-rules-table").querySelector("tbody")
    const row = tbody.insertRow()
    row.id = `rule-${tbody.rows.length}`;
    row.insertCell().textContent = category.value
    row.insertCell().textContent = regex.value
    row.insertCell().innerHTML = `<button class="btn btn-link p-0" onclick="delCategoryRule('${row.id}')"> <i class="bi bi-trash"></i> </button>`
    category.value = ''
    regex.value = ''
}
function delCategoryRule(id) {
    const row = document.getElementById(id)
    if(row) {
        row.remove()
    }
}
function commitCategoryRules() {
    const tbody = document.getElementById("edit-category-rules-table").querySelector("tbody")
    const rows = tbody.querySelectorAll("tr")
    categoryRules = []
    rows.forEach(row => {
        const cells = row.querySelectorAll("td")
        categoryRules.push([cells[0].textContent, cells[1].textContent])
    })

    fetch('/update_category_rules', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'
        },
        body: JSON.stringify({ rules: categoryRules })
    })
    .then(response => response.json())
    .then()
    .then(error => console.error('Error:', error))

}

// Validity rules
function validityRulesChange(input) {
    let category = input.dataset.category
    let tool = input.dataset.tool
    let state = input.dataset.state
    let request = new Request(`/set_validity_rule/${category}/${tool}/${state}`)
    fetch(request).catch(err => { console.log("Failed to update validity rules:", err)})
    refreshTab('devices', false) // TODO: overkill, should only reload the validity data
}
function validityRulesUpdateVisual(checkbox) {
    checkbox.checked = checkbox.dataset.state == "1";
    checkbox.indeterminate = checkbox.dataset.state == "2";
    checkbox.classList.remove('state-indeterminate', 'state-checked', 'state-unchecked')
    if(checkbox.checked) {
        checkbox.classList.add('state-checked')
    }
    else if(checkbox.indeterminate) {
        checkbox.classList.add('state-indeterminate')
    }
    else {
        checkbox.classList.add('state-unchecked')
    }
}
