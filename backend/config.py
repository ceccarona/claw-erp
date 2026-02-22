import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'claw-erp-secret-key-2024')
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'instance', 'claw_erp.db'))
JWT_EXPIRATION_HOURS = 24
