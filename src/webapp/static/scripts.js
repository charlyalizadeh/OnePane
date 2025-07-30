function updateTab(rows, tabId) {
    const table = `#${tabId}_table`;
    let dt;
    // Get the DataTable
    if(!$.fn.DataTable.isDataTable(table)) {
        dt = $(table).DataTable({
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            pageLength: 50,
            createdRow: function (row, data, dataIndex) {
                if(tabId != "devices") { return }
                const isValid = data[data.length - 1];
                if (isValid) {
                    $(row).addClass('row-valid');
                } else {
                    $(row).addClass('row-invalid');
                }
            }
        })
    }
    else {
        dt = $(table).DataTable();
        dt.clear();
    }
    // Setup the data
    rows.forEach((row, index) => {
        const rowData = [index + 1, ...Object.values(row)];
        dt.row.add(rowData);
    });
    dt.draw();
}

function refreshTab(tabId, update) {
    const btn = document.getElementById(`refresh-${tabId}`);
    const btnText = document.getElementById(`refresh-${tabId}-text`);

    btn.disabled = true;
    btnText.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`;

    if(update) {
        fetch(`/update_devices/${tabId}`)
    }
    fetch(`/get_devices/${tabId}`)
        .then(response => response.json())
        .then(data => {
            updateTab(data['rows'], tabId);

            btnText.innerHTML = '<i class="bi bi-check-lg"></i>';
            btn.classList.remove('btn-outline-primary')
            btn.classList.add('btn-outline-success')
            setTimeout(() => {
                btnText.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
                btn.disabled = false;
                btn.classList.remove('btn-outline-success')
                btn.classList.add('btn-outline-primary')
            }, 1500);
        })
        .catch(error => {
            console.error("Refresh failed:", error);
            btnText.innerHTML = `Error`;
            btn.classList.remove('btn-outline-primary')
            btn.classList.add('btn-outline-danger')
            setTimeout(() => {
                btnText.textContent = "Refresh";
                btn.disabled = false;
                btn.classList.remove('btn-outline-danger')
                btn.classList.add('btn-outline-primary')
            }, 1500);
        });
}

function validityRulesEdit(input) {
    let category = input.dataset.category
    let tool = input.dataset.tool
    let value = Number(input.checked)
    let request = new Request(`/set_validity_rule/${category}/${tool}/${value}`)
    fetch(request).catch(err => { console.log("Failed to update validity rules:", err)})
}
