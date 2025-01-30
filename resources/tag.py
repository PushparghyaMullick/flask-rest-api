from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from schemas import TagSchema, TagItemsSchema
from models import TagModel, StoreModel, ItemModel


blp = Blueprint("tags", __name__, description="Operations on tags")


@blp.route("/store/<int:store_id>/tag")
class TagStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A tag with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag, 201


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it",
        example={"message": "Tag deleted"}
    )
    @blp.alt_response(404, description="Tag not found")
    @blp.alt_response(
        400,
        description="If tag is assigned to some items, it is not deleted"
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            try:
                db.session.delete(tag)
                db.session.commit()
                return {"message": "Tag deleted"}
            except SQLAlchemyError:
                abort(500, message="An error occurred while deleting the tag")

        abort(400, message="Could not delete the tag. Make sure it is not associated with any item")


# Implement only for tags items of same store
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class TagItems(MethodView):
    @blp.response(201, TagSchema)
    @blp.alt_response(
        400,
        description="Item and tag from different stores can't be linked"
    )
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store_id != tag.store_id:
            abort(400, message="Item and tag should belong to the same store")

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "An error occurred while inserting the tag")

        return tag, 201
    
    @blp.response(200, TagItemsSchema)
    @blp.alt_response(
        404,
        description="Item and tag should be linked before unlinking"
    )
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag not in item.tags:
            abort(404, message="Item and tag should be linked before attempting to unlink")

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "An error occurred while removing the tag")

        return {"message": "Item removed from tag", "item": item}