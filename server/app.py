#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def home():
    return "<h1>Bakery GET-POST-PATCH-DELETE API</h1>"


@app.route("/bakeries")
def bakeries():
    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]

    response = make_response(bakeries_serialized, 200)
    return response


@app.route("/bakeries/<int:id>", methods=["GET", "PATCH"])
def bakery_by_id(id):
    bakery = Bakery.query.filter(Bakery.id == id).first()
    if bakery == None:
        return {}, 404
    elif request.method == "GET":
        bakery_serialized = bakery.to_dict()

        response = make_response(bakery_serialized, 200)
        return response
    elif request.method == "PATCH":
        data = request.json
        try:
            for attr in data:
                setattr(bakery, attr, data[attr])
            db.session.commit()
            return bakery.to_dict(), 200
        except (IntegrityError, ValueError) as ie:
            return {"error": ie.args}, 422


@app.route("/baked_goods/by_price", methods=["GET", "POST"])
def baked_goods_by_price():
    if request.method == "GET":
        baked_goods_by_price = BakedGood.query.order_by(BakedGood.price).all()
        baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]

        # response = make_response(baked_goods_by_price_serialized, 200)
        return baked_goods_by_price_serialized


@app.route("/baked_goods/most_expensive")
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()

    response = make_response(most_expensive_serialized, 200)
    return response


@app.route("/baked_goods", methods=["POST"])
def add_backed_good():
    if request.method == "POST":
        data = request.json
        baked_good = BakedGood()
        try:
            for attr in data:
                setattr(baked_good, attr, data[attr])
            db.session.add(baked_good)
            db.session.commit()
            return baked_good.to_dict(), 201
        except (IntegrityError, ValueError) as ie:
            return {"error": ie.args}, 422


@app.route("/baked_goods/<int:id>", methods=["DELETE"])
def del_baked_good(id):
    baked_good = BakedGood.query.filter(BakedGood.id == id).first()
    if baked_good == None:
        return {}, 404
    elif request.method == "DELETE":
        db.session.delete(baked_good)
        db.session.commit()
        return {}, 204


if __name__ == "__main__":
    app.run(port=5555, debug=True)
