import os
from flask import Flask, render_template, request, jsonify, Blueprint
from config_manager import ConfigManager

class WebGUI:
    """Class for web-based GUI."""

    def __init__(self, config_path="config.yaml",
                 template_dir="templates",
                 static_dir="static",
                 host="0.0.0.0",
                 port=5000):
        """
        Initialize the web GUI.

        Args:
            config_path: Path to configuration file
            template_dir: Directory containing templates
            static_dir: Directory containing static files
            host: Host to bind to
            port: Port to bind to
        """
        self.config_path = config_path
        self.template_dir = template_dir
        self.static_dir = static_dir
        self.host = host
        self.port = port
        self.config_manager = ConfigManager(config_path)

        # Create Blueprint for routes
        self.app = Blueprint('huizenzoeker', __name__)

        # Register routes
        self.register_routes()

    def register_routes(self):
        """Register Flask routes."""

        @self.app.route('/')
        def index():
            """Render index page."""
            return render_template('index.html')

        @self.app.route('/properties')
        def properties():
            """Render properties page."""
            return render_template('properties.html')

        @self.app.route('/settings')
        def settings():
            """Render settings page."""
            return render_template('settings.html')

        @self.app.route('/api/properties')
        def api_properties():
            """API endpoint for properties."""
            # This would be connected to the database in a real implementation
            return jsonify({'properties': []})

        @self.app.route('/api/settings', methods=['GET', 'POST'])
        def api_settings():
            """API endpoint for settings."""
            if request.method == 'POST':
                # Save settings
                settings = request.json
                try:
                    # Update config with new settings
                    for section, values in settings.items():
                        for key, value in values.items():
                            self.config_manager.set(section, key, value)

                    # Save config to file
                    if self.config_manager.save():
                        return jsonify({'success': True})
                    else:
                        return jsonify({'success': False, 'error': 'Failed to save configuration'})
                except Exception as e:
                    return jsonify({'success': False, 'error': str(e)})
            else:
                # Load settings
                try:
                    return jsonify({
                        'general': self.config_manager.get('general'),
                        'filter': self.config_manager.get('filter'),
                        'telegram': self.config_manager.get('telegram'),
                        'websites': self.config_manager.get('websites')
                    })
                except Exception as e:
                    return jsonify({'error': str(e)})

        @self.app.route('/api/run', methods=['POST'])
        def api_run():
            """API endpoint to run scraper manually."""
            # This would trigger the scraper in a real implementation
            return jsonify({'success': True, 'message': 'Scraper gestart'})

    def create_template_files(self):
        """Create template files if they don't exist."""
        # Create template directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)

        # Create static directory if it doesn't exist
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'js'), exist_ok=True)

        # Create index.html
        index_html = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Huizenzoeker</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Huizenzoeker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/properties">Woningen</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/settings">Instellingen</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Dashboard</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card text-white bg-primary mb-3">
                                    <div class="card-header">Nieuwe woningen</div>
                                    <div class="card-body">
                                        <h5 class="card-title" id="new-count">0</h5>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card text-white bg-success mb-3">
                                    <div class="card-header">Gewijzigde woningen</div>
                                    <div class="card-body">
                                        <h5 class="card-title" id="updated-count">0</h5>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card text-white bg-danger mb-3">
                                    <div class="card-header">Verwijderde woningen</div>
                                    <div class="card-body">
                                        <h5 class="card-title" id="removed-count">0</h5>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row mt-4">
                            <div class="col-md-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h5 class="card-title">Recente activiteit</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>Datum</th>
                                                        <th>Type</th>
                                                        <th>Adres</th>
                                                        <th>Prijs</th>
                                                        <th>Actie</th>
                                                    </tr>
                                                </thead>
                                                <tbody id="activity-table">
                                                    <tr>
                                                        <td colspan="5" class="text-center">Geen recente activiteit</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row mt-4">
                            <div class="col-md-12">
                                <button id="run-scraper" class="btn btn-primary">Scraper handmatig starten</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
</body>
</html>
        """

        # Create properties.html
        properties_html = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Woningen - Huizenzoeker</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Huizenzoeker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/properties">Woningen</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/settings">Instellingen</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="card-title mb-0">Woningen</h5>
                        <div>
                            <button class="btn btn-sm btn-outline-primary" id="filter-button">Filter</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="filter-panel mb-4" id="filter-panel" style="display: none;">
                            <div class="card">
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-3">
                                            <div class="mb-3">
                                                <label for="min-price" class="form-label">Minimale prijs</label>
                                                <input type="number" class="form-control" id="min-price" value="100000">
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="mb-3">
                                                <label for="max-price" class="form-label">Maximale prijs</label>
                                                <input type="number" class="form-control" id="max-price" value="225000">
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="mb-3">
                                                <label for="min-area" class="form-label">Minimale oppervlakte (m²)</label>
                                                <input type="number" class="form-control" id="min-area" value="0">
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="mb-3">
                                                <label for="city" class="form-label">Plaats</label>
                                                <input type="text" class="form-control" id="city">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-12">
                                            <button class="btn btn-primary" id="apply-filter">Filter toepassen</button>
                                            <button class="btn btn-outline-secondary" id="reset-filter">Reset</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Adres</th>
                                        <th>Plaats</th>
                                        <th>Prijs</th>
                                        <th>Oppervlakte</th>
                                        <th>Type</th>
                                        <th>Bron</th>
                                        <th>Actie</th>
                                    </tr>
                                </thead>
                                <tbody id="properties-table">
                                    <tr>
                                        <td colspan="7" class="text-center">Geen woningen gevonden</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div class="pagination-container mt-3 d-flex justify-content-between align-items-center">
                            <div>
                                <span id="showing-info">Toon 0-0 van 0 woningen</span>
                            </div>
                            <nav aria-label="Page navigation">
                                <ul class="pagination" id="pagination">
                                    <li class="page-item disabled">
                                        <a class="page-link" href="#" tabindex="-1">Vorige</a>
                                    </li>
                                    <li class="page-item active"><a class="page-link" href="#">1</a></li>
                                    <li class="page-item disabled">
                                        <a class="page-link" href="#">Volgende</a>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                    </div>
                </div>

(Content truncated due to size limit. Use line ranges to read in chunks)