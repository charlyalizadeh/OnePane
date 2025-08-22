// Button state
function setBtnStateLoad(btn, btnText) {
    btn.disabled = true
    btnText.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
}
function setBtnStateSuccess(btn, btnText) {
    btnText.innerHTML = '<i class="bi bi-check-lg"></i>'
    btn.classList.remove('btn-outline-primary')
    btn.classList.add('btn-outline-success')
    setTimeout(() => {
        btnText.innerHTML = '<i class="bi bi-arrow-clockwise"></i>'
        btn.disabled = false
        btn.classList.remove('btn-outline-success')
        btn.classList.add('btn-outline-primary')
    }, 1500)
}
function setBtnStateFailure(btn, btnText, error) {
    console.error("Refresh failed:", error)
    btnText.innerHTML = `Error`
    btn.classList.remove('btn-outline-primary')
    btn.classList.add('btn-outline-danger')
    setTimeout(() => {
        btnText.textContent = "Refresh"
        btn.disabled = false
        btn.classList.remove('btn-outline-danger')
        btn.classList.add('btn-outline-primary')
    }, 1500)
}

// DataTables data update
function updateTab(rows, tabId) {
    const trueDisplay = '<span style="color: green">✔</span>'
    const falseDisplay = '' //'<span style="color: red">✘</span>'
    const table = `#${tabId}-table`
    let dt
    // Get the DataTable
    if(!$.fn.DataTable.isDataTable(table)) {
        dt = $(table).DataTable({
            layout: {
                topStart: ['pageLength', 'buttons']
            },
            buttons: ['colvis'],
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            pageLength: 50,
            scrollX: true,
            fixedColumns: { start: 2 },
            colResize: { isEnabled: true },
            createdRow: function (row, data, dataIndex) {
                if(tabId != "devices") { return }
                const isValid = data[data.length - 1] == trueDisplay
                if (isValid) {
                    $(row).addClass('row-valid')
                } else {
                    $(row).addClass('row-invalid')
                }
            },
            headerCallback: function(thead) {
                $(thead).find('th').css({
                    'background-color': '#3b82f6',
                    'color': '#ffffff',
                    'border-bottom': 'none',
                    'padding': '0.75rem 1rem',
                    'text-align': 'left',
                    'font-weight': '600',
                    'border-radius': '0.5rem 0.5rem 0 0'
                })
            }
        })
    }
    else {
        dt = $(table).DataTable()
        dt.clear()
    }
    // Setup the data
    rows.forEach((row, index) => {
        const rowData = [index + 1, ...Object.values(row)]
        for(let i = 0; i < rowData.length; i++) {
            if(rowData[i] == true)
                rowData[i] = trueDisplay
            if(rowData[i] == false)
                rowData[i] = falseDisplay
        }
        dt.row.add(rowData)
    })
    dt.draw()
}
function refreshTab(tabId, update) {
    const btn = document.getElementById(`refresh-${tabId}`)
    const btnText = document.getElementById(`refresh-${tabId}-text`)

    setBtnStateLoad(btn, btnText)
    if(update) {
        fetch(`/update_devices/${tabId}`)
    }
    fetch(`/get_devices/${tabId}`)
        .then(response => response.json())
        .then(data => {
            updateTab(data['rows'], tabId)
            setBtnStateSuccess(btn, btnText)
        })
        .catch(error => {
            setBtnStateFailure(btn, btnText, error)
        })
}

// Validity rules
function validityRulesEdit(input) {
    let category = input.dataset.category
    let tool = input.dataset.tool
    let state = input.dataset.state
    let request = new Request(`/set_validity_rule/${category}/${tool}/${state}`)
    fetch(request).catch(err => { console.log("Failed to update validity rules:", err)})
}
