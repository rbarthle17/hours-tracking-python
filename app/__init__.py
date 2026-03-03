from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Register template helpers
    from app.helpers import register_helpers
    register_helpers(app)

    # Inject `now` and `request` into all templates
    import datetime
    from flask import request as flask_request

    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.datetime.now(),
            'timedelta': datetime.timedelta,
            'request': flask_request,
        }

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.clients import clients_bp
    from app.blueprints.contracts import contracts_bp
    from app.blueprints.tickets import tickets_bp
    from app.blueprints.timeentries import timeentries_bp
    from app.blueprints.invoices import invoices_bp
    from app.blueprints.payments import payments_bp
    from app.blueprints.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(timeentries_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(users_bp)

    return app
