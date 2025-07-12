import sys
from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS
from service import config
from service.common import log_handlers

app = Flask(__name__)
app.config.from_object('service.config')
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup security headers and CORS BEFORE importing routes
talisman = Talisman(app, force_https=False)  # Disable HTTPS redirect if desired
CORS(app)

# Import routes after app and middleware are setup
from service import routes, models  # noqa: F401 E402
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Setup logging
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    sys.exit(4)

app.logger.info("Service initialized!")
