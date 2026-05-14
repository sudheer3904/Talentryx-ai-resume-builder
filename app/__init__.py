from flask import Flask, render_template
from flask_mail import Mail
from config import Config

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    mail.init_app(app)

    # Initialize Database
    from app.database import db
    db.init_app(app)

    # Register Blueprints
    from app.routes import auth
    app.register_blueprint(auth.bp)
    
    # from app.routes import resume, analysis, interview
    from app.routes import resume
    app.register_blueprint(resume.bp)
    
    from app.routes import analysis
    app.register_blueprint(analysis.bp)
    
    from app.routes import interview
    app.register_blueprint(interview.bp)

    from app.routes import admin
    app.register_blueprint(admin.bp)

    from app.routes import multi_career
    app.register_blueprint(multi_career.bp)
    
    from app.routes import ai
    app.register_blueprint(ai.bp)
    
    @app.route('/')
    def index():
        return render_template('landing.html')

    return app
