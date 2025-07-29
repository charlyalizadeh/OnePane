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

function validityRulesEdit(input) {
    let category = input.dataset.category
    let tool = input.dataset.tool
    let value = Number(input.checked)
    let request = new Request(`/set_validity_rule/${category}/${tool}/${value}`)
    fetch(request).catch(err => { console.log("Failed to update validity rules:", err)})
}
