from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


roles_users = db.Table(
    'roles_users',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('roles_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
) 


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', secondary="roles_users")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    roles = db.relationship('Role', secondary="roles_users")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def serialize_with_roles(self):
        return {
            "id": self.id,
            "name": self.name,
            "roles": self.get_roles()
        }

    def get_roles(self):
        return list(map(lambda role: role.serialize(), self.roles))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    
""" 
class RoleUser(db.Model):
    __tablename__ = 'roles_users'
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    roles_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

    def serialize(self):
        return {
            "users_id": self.users_id,
            "roles_id": self.roles_id
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit() 
"""