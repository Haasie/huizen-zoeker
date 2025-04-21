document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap Modal instances
    const realtorModal = new bootstrap.Modal(document.getElementById('realtor-modal'));
    const deleteModal = new bootstrap.Modal(document.getElementById('delete-modal'));
    
    // Sample data for realtors (in a real app, this would come from the server)
    const realtors = [
        {
            id: 'klipenvw',
            name: 'Klip & VW',
            website: 'klipenvw.nl',
            searchUrl: 'https://www.klipenvw.nl/aanbod/woningaanbod/',
            listingSelector: '.property-item',
            titleSelector: '.property-title',
            priceSelector: '.property-price',
            areaSelector: '.property-area',
            roomsSelector: '.property-rooms',
            linkSelector: '.property-link',
            citySelector: '.property-city',
            active: true,
            notes: ''
        },
        {
            id: 'bijdevaate',
            name: 'Bij de Vaate Makelaardij',
            website: 'bijdevaatemakelaardij.nl',
            searchUrl: 'https://www.bijdevaatemakelaardij.nl/aanbod',
            listingSelector: '.property-item',
            titleSelector: '.property-title',
            priceSelector: '.property-price',
            areaSelector: '.property-area',
            roomsSelector: '.property-rooms',
            linkSelector: '.property-link',
            citySelector: '.property-city',
            active: true,
            notes: ''
        },
        {
            id: 'ooms',
            name: 'Ooms Makelaars',
            website: 'ooms.com',
            searchUrl: 'https://www.ooms.com/woningaanbod',
            listingSelector: '.property-item',
            titleSelector: '.property-title',
            priceSelector: '.property-price',
            areaSelector: '.property-area',
            roomsSelector: '.property-rooms',
            linkSelector: '.property-link',
            citySelector: '.property-city',
            active: true,
            notes: ''
        },
        {
            id: 'vbrmakelaars',
            name: 'VBR Makelaars',
            website: 'vbrmakelaars.nl',
            searchUrl: 'https://www.vbrmakelaars.nl/aanbod',
            listingSelector: '.property-item',
            titleSelector: '.property-title',
            priceSelector: '.property-price',
            areaSelector: '.property-area',
            roomsSelector: '.property-rooms',
            linkSelector: '.property-link',
            citySelector: '.property-city',
            active: true,
            notes: ''
        },
        {
            id: 'ruimzicht',
            name: 'Ruimzicht Makelaardij',
            website: 'ruimzicht.nl',
            searchUrl: 'https://www.ruimzicht.nl/woningen',
            listingSelector: '.property-item',
            titleSelector: '.property-title',
            priceSelector: '.property-price',
            areaSelector: '.property-area',
            roomsSelector: '.property-rooms',
            linkSelector: '.property-link',
            citySelector: '.property-city',
            active: true,
            notes: ''
        }
    ];
    
    // Function to render the realtors table
    function renderRealtorsTable() {
        const tableBody = document.getElementById('realtors-table');
        tableBody.innerHTML = '';
        
        realtors.forEach(realtor => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${realtor.name}</td>
                <td>${realtor.website}</td>
                <td>${realtor.searchUrl}</td>
                <td><span class="badge ${realtor.active ? 'bg-success' : 'bg-secondary'}">${realtor.active ? 'Actief' : 'Inactief'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-realtor" data-id="${realtor.id}">Bewerken</button>
                    <button class="btn btn-sm btn-outline-danger delete-realtor" data-id="${realtor.id}">Verwijderen</button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Add event listeners to edit and delete buttons
        document.querySelectorAll('.edit-realtor').forEach(button => {
            button.addEventListener('click', function() {
                const realtorId = this.getAttribute('data-id');
                editRealtor(realtorId);
            });
        });
        
        document.querySelectorAll('.delete-realtor').forEach(button => {
            button.addEventListener('click', function() {
                const realtorId = this.getAttribute('data-id');
                deleteRealtor(realtorId);
            });
        });
    }
    
    // Function to open the add realtor modal
    function addRealtor() {
        // Clear the form
        document.getElementById('realtor-modal-label').textContent = 'Makelaar Toevoegen';
        document.getElementById('realtor-form').reset();
        document.getElementById('realtor-id').value = '';
        
        // Show the modal
        realtorModal.show();
    }
    
    // Function to open the edit realtor modal
    function editRealtor(realtorId) {
        // Find the realtor
        const realtor = realtors.find(r => r.id === realtorId);
        if (!realtor) return;
        
        // Set the form values
        document.getElementById('realtor-modal-label').textContent = 'Makelaar Bewerken';
        document.getElementById('realtor-id').value = realtor.id;
        document.getElementById('realtor-name').value = realtor.name;
        document.getElementById('realtor-website').value = realtor.website;
        document.getElementById('realtor-search-url').value = realtor.searchUrl;
        document.getElementById('realtor-listing-selector').value = realtor.listingSelector;
        document.getElementById('realtor-title-selector').value = realtor.titleSelector;
        document.getElementById('realtor-price-selector').value = realtor.priceSelector;
        document.getElementById('realtor-area-selector').value = realtor.areaSelector;
        document.getElementById('realtor-rooms-selector').value = realtor.roomsSelector;
        document.getElementById('realtor-link-selector').value = realtor.linkSelector;
        document.getElementById('realtor-city-selector').value = realtor.citySelector;
        document.getElementById('realtor-active').checked = realtor.active;
        document.getElementById('realtor-notes').value = realtor.notes;
        
        // Show the modal
        realtorModal.show();
    }
    
    // Function to save a realtor
    function saveRealtor() {
        // Get the form values
        const realtorId = document.getElementById('realtor-id').value;
        const name = document.getElementById('realtor-name').value;
        const website = document.getElementById('realtor-website').value;
        const searchUrl = document.getElementById('realtor-search-url').value;
        const listingSelector = document.getElementById('realtor-listing-selector').value;
        const titleSelector = document.getElementById('realtor-title-selector').value;
        const priceSelector = document.getElementById('realtor-price-selector').value;
        const areaSelector = document.getElementById('realtor-area-selector').value;
        const roomsSelector = document.getElementById('realtor-rooms-selector').value;
        const linkSelector = document.getElementById('realtor-link-selector').value;
        const citySelector = document.getElementById('realtor-city-selector').value;
        const active = document.getElementById('realtor-active').checked;
        const notes = document.getElementById('realtor-notes').value;
        
        // Validate required fields
        if (!name || !website || !searchUrl || !listingSelector) {
            alert('Vul alle verplichte velden in');
            return;
        }
        
        // Create a new realtor object
        const newRealtor = {
            id: realtorId || website.replace(/[^a-z0-9]/gi, '').toLowerCase(),
            name,
            website,
            searchUrl,
            listingSelector,
            titleSelector,
            priceSelector,
            areaSelector,
            roomsSelector,
            linkSelector,
            citySelector,
            active,
            notes
        };
        
        // Check if we're editing an existing realtor or adding a new one
        if (realtorId) {
            // Update existing realtor
            const index = realtors.findIndex(r => r.id === realtorId);
            if (index !== -1) {
                realtors[index] = newRealtor;
            }
        } else {
            // Add new realtor
            realtors.push(newRealtor);
        }
        
        // Hide the modal
        realtorModal.hide();
        
        // Update the table
        renderRealtorsTable();
        
        // Show success message
        alert(`Makelaar "${name}" is ${realtorId ? 'bijgewerkt' : 'toegevoegd'}`);
        
        // In a real app, we would save to the server here
        saveToServer(realtors);
    }
    
    // Function to delete a realtor
    function deleteRealtor(realtorId) {
        // Find the realtor
        const realtor = realtors.find(r => r.id === realtorId);
        if (!realtor) return;
        
        // Set up the delete confirmation
        document.getElementById('delete-modal-label').textContent = `Makelaar "${realtor.name}" Verwijderen`;
        
        // Set up the confirm delete button
        const confirmDeleteButton = document.getElementById('confirm-delete');
        confirmDeleteButton.onclick = function() {
            // Remove the realtor from the array
            const index = realtors.findIndex(r => r.id === realtorId);
            if (index !== -1) {
                realtors.splice(index, 1);
            }
            
            // Hide the modal
            deleteModal.hide();
            
            // Update the table
            renderRealtorsTable();
            
            // Show success message
            alert(`Makelaar "${realtor.name}" is verwijderd`);
            
            // In a real app, we would save to the server here
            saveToServer(realtors);
        };
        
        // Show the modal
        deleteModal.show();
    }
    
    // Function to save to server (mock implementation)
    function saveToServer(data) {
        console.log('Saving to server:', data);
        // In a real app, this would be an API call
        localStorage.setItem('realtors', JSON.stringify(data));
    }
    
    // Add event listener to the add realtor button
    document.getElementById('add-realtor-button').addEventListener('click', addRealtor);
    
    // Add event listener to the save realtor button
    document.getElementById('save-realtor').addEventListener('click', saveRealtor);
    
    // Initial render
    renderRealtorsTable();
    
    // Load from localStorage if available (simulating server data)
    const savedRealtors = localStorage.getItem('realtors');
    if (savedRealtors) {
        try {
            const parsedRealtors = JSON.parse(savedRealtors);
            // Replace the realtors array with the saved data
            realtors.length = 0;
            parsedRealtors.forEach(realtor => realtors.push(realtor));
            renderRealtorsTable();
        } catch (e) {
            console.error('Error parsing saved realtors:', e);
        }
    }
});
