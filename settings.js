document.addEventListener('DOMContentLoaded', function() {
    // Load current settings
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            if (settings.general) {
                document.getElementById('interval').value = settings.general.scan_interval || 30;
            }
            if (settings.filter) {
                document.getElementById('min-price').value = settings.filter.min_price || 100000;
                document.getElementById('max-price').value = settings.filter.max_price || 225000;
                document.getElementById('min-area').value = settings.filter.min_area || 0;
                document.getElementById('cities').value = settings.filter.cities ? settings.filter.cities.join(', ') : '';
            }
            if (settings.telegram) {
                document.getElementById('telegram-token').value = settings.telegram.token || '8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA';
                document.getElementById('telegram-chat-id').value = settings.telegram.chat_id || '';
            }
            if (settings.websites) {
                const checkboxes = document.querySelectorAll('input[name="websites"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = settings.websites[checkbox.value] || false;
                });
            }
        })
        .catch(error => console.error('Error loading settings:', error));

    // Handle form submission
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Collect form data
            const formData = {
                general: {
                    scan_interval: parseInt(document.getElementById('interval').value) || 30
                },
                filter: {
                    min_price: parseInt(document.getElementById('min-price').value) || 100000,
                    max_price: parseInt(document.getElementById('max-price').value) || 225000,
                    min_area: parseInt(document.getElementById('min-area').value) || 0,
                    cities: document.getElementById('cities').value.split(',').map(city => city.trim()).filter(city => city)
                },
                telegram: {
                    token: document.getElementById('telegram-token').value,
                    chat_id: document.getElementById('telegram-chat-id').value
                },
                websites: {}
            };

            // Add website settings
            const checkboxes = document.querySelectorAll('input[name="websites"]');
            checkboxes.forEach(checkbox => {
                formData.websites[checkbox.value] = checkbox.checked;
            });

            // Save settings
            fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Instellingen opgeslagen!');
                } else {
                    alert('Fout bij opslaan van instellingen: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error saving settings:', error);
                alert('Fout bij opslaan van instellingen');
            });
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
