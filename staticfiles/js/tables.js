window.onload = function() {
    const tenant = getTenantFromHostname();
    let isDragMode = false;

    loadTables(tenant);
    window.addEventListener('resize', () => loadTables(tenant));

    document.getElementById('toggle-drag-mode').addEventListener('click', () => {
        isDragMode = !isDragMode;
        toggleDragMode(isDragMode);
        document.getElementById('toggle-drag-mode').classList.toggle('active', isDragMode);
    });

    document.getElementById('arrange-buttons').addEventListener('click', arrangeButtons);

    function toggleDragMode(enable) {
        const buttons = document.querySelectorAll('.tables-container a');
        buttons.forEach(button => {
            if (enable) {
                enableDrag(button);
                button.style.border = '4px dashed yellow';
            } else {
                button.draggable = false;
                button.style.border = 'none';
            }
        });

        const container = document.querySelector('.tables-container');
        if (enable) {
            container.addEventListener('dragover', dragOverHandler);
            container.addEventListener('drop', dropHandler);
        } else {
            container.removeEventListener('dragover', dragOverHandler);
            container.removeEventListener('drop', dropHandler);
        }
    }

    function enableDrag(element) {
        element.draggable = true;
        element.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', e.target.id);
        });
    }

    function dragOverHandler(event) {
        event.preventDefault();
    }

    function dropHandler(event) {
        event.preventDefault();
        const id = event.dataTransfer.getData('text/plain');
        const draggableElement = document.getElementById(id);
        const rect = event.currentTarget.getBoundingClientRect();
        const x = event.clientX - rect.left - draggableElement.clientWidth / 2;
        const y = event.clientY - rect.top - draggableElement.clientHeight / 2;
        draggableElement.style.left = `${x}px`;
        draggableElement.style.top = `${y}px`;
        event.dataTransfer.clearData();
        saveButtonPosition(id, x, y);
    }

    function arrangeButtons() {
        const container = document.querySelector('.tables-container');
        const buttons = Array.from(container.querySelectorAll('a'));
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const buttonSize = Math.min(containerWidth, containerHeight) / 4.5;
        const margin = buttonSize / 8;

        buttons.sort((a, b) => parseInt(a.id.split('-')[1], 10) - parseInt(b.id.split('-')[1], 10));

        buttons.forEach((button, index) => {
            const x = (index % 5) * (buttonSize + margin);
            const y = Math.floor(index / 5) * (buttonSize + margin);
            button.style.left = `${x}px`;
            button.style.top = `${y}px`;
            saveButtonPosition(button.id, x, y);
        });
    }

    async function loadTables(tenant) {
        try {
            const url = `/tenants_folders/${tenant}_upload_json/occupied_tables.json`;
            const response = await fetch(url);
            const tables = await response.json();

            const positions = await loadButtonPositions();
            createTableButtons(tables, positions);
        } catch (error) {
            console.error('Error loading tables:', error);
        }
    }

    async function saveButtonPosition(id, x, y) {
        const positions = JSON.parse(localStorage.getItem('buttonPositions')) || {};
        positions[id] = { x, y };
        localStorage.setItem('buttonPositions', JSON.stringify(positions));

        try {
            await fetch('/save_positions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(positions)
            });
        } catch (error) {
            console.error('Error saving positions:', error);
        }
    }

    async function loadButtonPositions() {
        try {
            const response = await fetch('/load_positions');
            const positions = await response.json();
            localStorage.setItem('buttonPositions', JSON.stringify(positions));
            return positions;
        } catch (error) {
            console.error('Error loading positions:', error);
            return JSON.parse(localStorage.getItem('buttonPositions')) || {};
        }
    }

    function createTableButtons(tables, positions) {
        const container = document.querySelector('.tables-container');
        container.innerHTML = '';
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const buttonSize = Math.min(containerWidth, containerHeight) / 5;
        const fontSize = buttonSize / 5;
        const margin = buttonSize / 8;
    
        tables.tables.forEach((table) => {
            const button = document.createElement('a');
            button.id = `table-${table.table_number}`;
            button.href = `/table_orders/${getTenantFromHostname()}/${table.table_number}/`;
            button.className = 'table-button';
    
            button.style.width = `${buttonSize}px`;
            button.style.height = `${buttonSize}px`;
    
            if (positions[button.id]) {
                button.style.left = `${positions[button.id].x}px`;
                button.style.top = `${positions[button.id].y}px`;
            }
    
            // Δημιουργία του αριθμού τραπεζιού
            const tableNumberDiv = document.createElement('div');
            tableNumberDiv.className = 'table-number';
            tableNumberDiv.textContent = `Table ${table.table_number}`;
            button.appendChild(tableNumberDiv);
    
            // Έλεγχος αν υπάρχει κρατήση ή παραγγελία
            if (table.order_status) {
                // Αλλαγή χρώματος για τραπέζι με παραγγελία
                button.style.backgroundColor = '#4CAF50';  // Πράσινο για παραγγελίες
                const statusBannerDiv = document.createElement('div');
                statusBannerDiv.className = 'status-banner';
                statusBannerDiv.textContent = 'Order In Progress';
                button.appendChild(statusBannerDiv);
            } else if (table.reservation_status) {
                // Αλλαγή χρώματος για τραπέζι με κρατήση
                button.style.backgroundColor = '#FFC107';  // Κίτρινο για κρατήσεις
                const reservedBannerDiv = document.createElement('div');
                reservedBannerDiv.className = 'reserved-banner';
                reservedBannerDiv.textContent = 'Reserved';
                button.appendChild(reservedBannerDiv);
            } else {
                // Προκαθορισμένο χρώμα για ελεύθερα τραπέζια
                button.style.backgroundColor = '#FF5722';  // Κόκκινο για ελεύθερα τραπέζια
            }
    
            // Προσθήκη του χρόνου εξυπηρέτησης, αν υπάρχει
            if (table.time_diff) {
                const timeDiffDiv = document.createElement('div');
                timeDiffDiv.className = 'time-diff';
                timeDiffDiv.textContent = `Served ${table.time_diff}`;
                button.appendChild(timeDiffDiv);
            }
    
            container.appendChild(button);
        });
    }
}