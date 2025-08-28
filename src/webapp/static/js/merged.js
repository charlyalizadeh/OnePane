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
    let request = new Request(`/set_category_rule/${category.value}/${regex.value}`)
    fetch(request).catch(err => { console.log("Failed to update category rules:", err) })
    refreshTabDevices('devices', false)

    category.value = ''
    regex.value = ''
}
function delCategoryRule(id) {
    const row = document.getElementById(id)
    if(row) {
        const category = row.querySelector('td')
        let request = new Request(`/del_category_rule/${category.innerText}`)
        fetch(request).catch(err => { console.log("Failed to update category rules:", err) })
        refreshTabDevices('devices', false)
        row.remove()
    }
}

// Validity rules
function validityRulesModalUpdateHead(json) {
    const thead = document.getElementById("edit-validity-rules-thead")

    // Clear the head
    thead.innerHTML = ''

    // Add a row
    const tr = document.createElement("tr")
    thead.appendChild(tr)

    // Add the category
    var th = document.createElement("th") 
    tr.appendChild(th)
    th.innerText = "Category"

    // Add the modules column
    json["activated_modules"].forEach(el => {
        th = document.createElement("th")
        th.innerText = el.display_name
        tr.appendChild(th)
    })
}
function validityRulesModalUpdateBody(json) {
    const tbody = document.getElementById("edit-validity-rules-tbody")

    // Clea the body
    tbody.innerHTML = ''
    for(const category in json["rules"]) {
        if(json["rules"].hasOwnProperty(category)) {
            // Add a row
            const tr = document.createElement("tr")
            tbody.appendChild(tr)

            // Add category
            const td_category = document.createElement("td")
            tr.appendChild(td_category)
            td_category.innerText = category

            // Retrieve the rules
            var rules = json["rules"][category]

            // Add the rules
            for(const module in rules) {
                if(rules.hasOwnProperty(module)) {
                    var value = rules[module]

                    // Add rules input
                    const td = document.createElement("td")
                    td.innerHTML = `<input
                                        type="checkbox"
                                        id="${category}_${module}"
                                        data-category="${category}"
                                        data-tool="${module}"
                                        data-state=${value}
                                        class="three-state"
                                    />`
                    tr.appendChild(td)
                }
            }
            tbody.appendChild(tr)
        }
    }
}
function validityRulesChange(input) {
    let category = input.dataset.category
    let tool = input.dataset.tool
    let state = input.dataset.state
    let request = new Request(`/set_validity_rule/${category}/${tool}/${state}`)
    fetch(request).catch(err => {console.log("Failed to update validity rules:", err)})
    refreshTabDevices('devices', false) // TODO: overkill, should only reload the validity data
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
function validityRulesModalUpdate() {
    // Retrieve the validity rules
    fetch("/get_validity_rules")
    .then(response => response.json())
    .then(json => {
        // Setup the input table
        validityRulesModalUpdateHead(json)
        validityRulesModalUpdateBody(json)

        // Setup the three state inputs event
        document.querySelectorAll('.three-state').forEach((checkbox) => {
            validityRulesUpdateVisual(checkbox)
            checkbox.addEventListener('click', (e) => {
                e.preventDefault();
                checkbox.dataset.state = (checkbox.dataset.state + 1) % 3;
                validityRulesUpdateVisual(checkbox)
                validityRulesChange(checkbox)
            });
        })
    })
}
