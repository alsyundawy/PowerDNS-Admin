from .base import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(128))
    users = db.relationship('User', back_populates='role', lazy=True)
    apikeys = db.relationship('ApiKey', back_populates='role', lazy=True)

    def __init__(self, id=None, name=None, description=None):
        # ``id`` stays optional so the database autoincrement keeps assigning
        # it when the caller does not supply one.
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Role {0}>'.format(self.name)

    @classmethod
    def get_id_by_name(cls, name):
        role = cls.query.filter_by(name=name).first()
        if not role:
            role = cls(name=name, description=name)
            db.session.add(role)
            db.session.commit()
        return role.id
