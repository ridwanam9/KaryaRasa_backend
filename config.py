import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres.qqxwgvcakthdawooayak:Ridwan9++@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
