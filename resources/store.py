from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import StoreModel
from schemas import StoreSchema
from db import db


blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)   
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        try:
            db.session.delete(store)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the store")

        return {"message": "Store deleted"}, 204


@blp.route("/store")
class Stores(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the store")

        return store, 201