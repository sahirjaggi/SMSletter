from app import db

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), index=True, unique=True)

    def __repr__(self):
        return '<Subscriber %r>' % (self.phone)
