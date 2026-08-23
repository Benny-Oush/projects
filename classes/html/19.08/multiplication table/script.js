const rowSize = document.getElementById('row')
const columnSize = document.getElementById('column')
const container = document.getElementById('container')
const button = document.getElementById('create').addEventListener('click', () => {
    container.innerHTML = ''
    for (let i = 0; i < rowSize.value; i++) {
        const row = document.createElement('div')
        row.classList.add('row')
        for (let j = 0; j < columnSize.value; j++) {
            const cell = document.createElement('div')
            cell.classList.add('cell')
            if (i == 0 || j == 0) {
                cell.classList.add('header')
            }
            cell.textContent = (i + 1) * (j + 1)
            row.appendChild(cell) 
        }
        container.appendChild(row)
    }
})