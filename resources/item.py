from flask.views import MethodView
from flask_smorest import abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel
from db import db


blp = Blueprint("items", __name__, description="Operations on items")
# A blueprint is a way to organize related views. It is a collection of routes and other configurations that are registered on the application.


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required")

        item = ItemModel.query.get_or_404(item_id)
        
        try:
            db.session.delete(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the item")

        return {"message": "Item deleted"}, 204


    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        # Prevents idempotency issues by checking if the item exists
        item = ItemModel.query.get(item_id)

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(400, message="An item with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the item")

        return item


@blp.route("/item")
class Items(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        # input data is validated against the ItemSchema and passed as item_data
        item = ItemModel(**item_data)

        try:
            db.session.add(item)  # adds item to session
            db.session.commit()  # commits item to db
        except IntegrityError:
            abort(400, message="An item with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")

        return item, 201