from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, subject, price):
        self.subject = subject
        self.price = price
        self.is_paid = False

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'price': self.price,
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Account {self.subject}: {self.price}>'

