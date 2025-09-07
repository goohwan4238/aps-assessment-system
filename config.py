import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aps-assessment-secret-key-2024'
    DATABASE_PATH = '/app/data/aps_assessment.db'