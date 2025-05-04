from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AliasRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_email = db.Column(db.String(120), nullable=False)
    alias = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
