document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Collect form data
            const formData = {
                interval: parseInt(document.getElementById('interval').value) || 30,
                min_price: parseInt(document.getElementById('min-price').value) || 100000,
                max_price: parseInt(document.getElementById('max-price').value) || 225000,
                min_area: parseInt(document.getElementById('min-area').value) || 0,
                cities: document.getElementById('cities').value.split(',').map(city => city.trim()).filter(city => city),
                telegram_token: document.getElementById('telegram-token').value,
                telegram_chat_id: document.getElementById('telegram-chat-id').value,
                websites: Array.from(document.querySelectorAll('input[name="websites"]:checked')).map(checkbox => checkbox.value)
            };
            
            alert('Instellingen opgeslagen!');
        });
    }
    
    // Handle reset button
    const resetSettingsButton = document.getElementById('reset-settings');
    if (resetSettingsButton) {
        resetSettingsButton.addEventListener('click', function() {
            if (confirm('Weet je zeker dat je alle instellingen wilt resetten naar de standaardwaarden?')) {
                document.getElementById('interval').value = '30';
                document.getElementById('min-price').value = '100000';
                document.getElementById('max-price').value = '225000';
                document.getElementById('min-area').value = '0';
                document.getElementById('cities').value = '';
                document.getElementById('telegram-token').value = '8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA';
                document.getElementById('telegram-chat-id').value = '';
                
                // Check all websites
                const checkboxes = document.querySelectorAll('input[name="websites"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = true;
                });
            }
        });
    }
    
    // Handle select/deselect all websites
    const selectAllButton = document.getElementById('select-all-websites');
    if (selectAllButton) {
        selectAllButton.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[name="websites"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });
    }
    
    const deselectAllButton = document.getElementById('deselect-all-websites');
    if (deselectAllButton) {
        deselectAllButton.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[name="websites"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        });
    }
});
