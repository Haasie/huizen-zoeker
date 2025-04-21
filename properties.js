document.addEventListener('DOMContentLoaded', function() {
    // Toggle filter panel
    const filterButton = document.getElementById('filter-button');
    if (filterButton) {
        filterButton.addEventListener('click', function() {
            const filterPanel = document.getElementById('filter-panel');
            if (filterPanel.style.display === 'none') {
                filterPanel.style.display = 'block';
            } else {
                filterPanel.style.display = 'none';
            }
        });
    }
    
    // Apply filter
    const applyFilterButton = document.getElementById('apply-filter');
    if (applyFilterButton) {
        applyFilterButton.addEventListener('click', function() {
            const minPrice = parseInt(document.getElementById('min-price').value) || 0;
            const maxPrice = parseInt(document.getElementById('max-price').value) || Number.MAX_SAFE_INTEGER;
            const minArea = parseInt(document.getElementById('min-area').value) || 0;
            const city = document.getElementById('city').value.toLowerCase();
            
            alert(`Filter toegepast: Prijs €${minPrice} - €${maxPrice}, Min. oppervlakte: ${minArea}m², Plaats: ${city || 'Alle'}`);
        });
    }
    
    // Reset filter
    const resetFilterButton = document.getElementById('reset-filter');
    if (resetFilterButton) {
        resetFilterButton.addEventListener('click', function() {
            document.getElementById('min-price').value = '100000';
            document.getElementById('max-price').value = '225000';
            document.getElementById('min-area').value = '0';
            document.getElementById('city').value = '';
            
            alert('Filters gereset naar standaardwaarden');
        });
    }
    
    // Pagination
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        if (!link.parentElement.classList.contains('disabled')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all page items
                document.querySelectorAll('.pagination .page-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active class to clicked page item
                this.parentElement.classList.add('active');
                
                // Update showing info
                if (this.textContent === 'Vorige' || this.textContent === 'Volgende') {
                    // Handle previous/next navigation
                } else {
                    const page = parseInt(this.textContent);
                    const startIndex = (page - 1) * 5 + 1;
                    const endIndex = Math.min(startIndex + 4, 50);
                    document.getElementById('showing-info').textContent = `Toon ${startIndex}-${endIndex} van 50 woningen`;
                }
            });
        }
    });
});
