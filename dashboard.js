document.addEventListener('DOMContentLoaded', function() {
    // Mock data for demonstration
    const mockData = {
        counts: {
            new: 5,
            updated: 3,
            removed: 1
        },
        activity: [
            {
                date: '2025-04-17 08:30:00',
                type: 'new',
                address: 'Voorbeeldstraat 123',
                city: 'Rotterdam',
                price: 215000,
                url: '#'
            },
            {
                date: '2025-04-17 08:25:00',
                type: 'updated',
                address: 'Testlaan 45',
                city: 'Hellevoetsluis',
                price: 189000,
                url: '#'
            },
            {
                date: '2025-04-17 08:20:00',
                type: 'removed',
                address: 'Demoweg 67',
                city: 'Rotterdam',
                price: 205000,
                url: '#'
            }
        ]
    };
    
    // Update counts
    document.getElementById('new-count').textContent = mockData.counts.new;
    document.getElementById('updated-count').textContent = mockData.counts.updated;
    document.getElementById('removed-count').textContent = mockData.counts.removed;
    
    // Update activity table
    const activityTable = document.getElementById('activity-table');
    if (activityTable.innerHTML.trim() === '') {
        mockData.activity.forEach(item => {
            const row = document.createElement('tr');
            
            // Format date
            const date = new Date(item.date);
            const formattedDate = date.toLocaleString('nl-NL');
            
            // Format price
            const formattedPrice = '€ ' + item.price.toLocaleString('nl-NL');
            
            // Determine type label and class
            let typeLabel, typeClass;
            if (item.type === 'new') {
                typeLabel = 'Nieuw';
                typeClass = 'badge bg-primary';
            } else if (item.type === 'updated') {
                typeLabel = 'Gewijzigd';
                typeClass = 'badge bg-success';
            } else {
                typeLabel = 'Verwijderd';
                typeClass = 'badge bg-danger';
            }
            
            row.innerHTML = `
                <td>${formattedDate}</td>
                <td><span class="${typeClass}">${typeLabel}</span></td>
                <td>${item.address}, ${item.city}</td>
                <td>${formattedPrice}</td>
                <td><a href="${item.url}" class="btn btn-sm btn-outline-primary">Bekijken</a></td>
            `;
            
            activityTable.appendChild(row);
        });
    }
    
    // Handle run scraper button
    const runScraperButton = document.getElementById('run-scraper');
    if (runScraperButton) {
        runScraperButton.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Bezig...';
            
            // Simulate API call
            setTimeout(() => {
                alert('Scraper is gestart. Resultaten zullen binnenkort beschikbaar zijn.');
                this.disabled = false;
                this.innerHTML = 'Scraper handmatig starten';
            }, 2000);
        });
    }
});
