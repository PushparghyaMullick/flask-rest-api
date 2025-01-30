from db import db


class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    items = db.relationship('ItemModel', lazy='dynamic', back_populates='store', cascade='all, delete')
    # grabs all items of this store
    # lazy=dynamic: items not fetched from db until told to
    tags = db.relationship('TagModel', back_populates='store', lazy='dynamic')
