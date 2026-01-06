#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route("/")
def index():
    return "Bakeries API"


# ---------------------------------------------------------
# BAKERIES
# GET /bakeries  -> list bakeries
# GET /bakeries/<id> -> single bakery
# PATCH /bakeries/<id> -> update bakery name (FORM DATA)
# ---------------------------------------------------------

@app.route("/bakeries", methods=["GET"])
def bakeries():
    bakeries_list = [b.to_dict() for b in Bakery.query.all()]
    return make_response(bakeries_list, 200)


@app.route("/bakeries/<int:id>", methods=["GET", "PATCH"])
def bakery_by_id(id):
    bakery = Bakery.query.filter(Bakery.id == id).first()

    if bakery is None:
        return make_response({"message": "Bakery not found"}, 404)

    # GET one bakery
    if request.method == "GET":
        return make_response(bakery.to_dict(), 200)

    # PATCH: update only provided fields (lab specifically: name)
    if request.method == "PATCH":
        # Request sends data in a form (x-www-form-urlencoded or form-data)
        new_name = request.form.get("name")
        if new_name is not None:
            bakery.name = new_name

        db.session.commit()
        return make_response(bakery.to_dict(), 200)



# BAKED GOODS
# GET /baked_goods -> list baked goods
# POST /baked_goods -> create baked good (FORM DATA)
# GET /baked_goods/<id> -> single baked good
# DELETE /baked_goods/<id> -> delete baked good


@app.route("/baked_goods", methods=["GET", "POST"])
def baked_goods():
    # GET all baked goods
    if request.method == "GET":
        baked_goods_list = [bg.to_dict() for bg in BakedGood.query.all()]
        return make_response(baked_goods_list, 200)

    # POST create baked good (FORM)
    if request.method == "POST":
        # Request sends data in a form
        name = request.form.get("name")
        price = request.form.get("price")
        bakery_id = request.form.get("bakery_id")

        # Basic required field check (safe for tests; won’t break normal flow)
        missing = []
        if name is None:
            missing.append("name")
        if price is None:
            missing.append("price")
        if bakery_id is None:
            missing.append("bakery_id")

        if missing:
            return make_response(
                {"message": "Missing required fields", "missing": missing},
                400
            )

        new_baked_good = BakedGood(
            name=name,
            price=price,
            bakery_id=bakery_id
        )

        db.session.add(new_baked_good)
        db.session.commit()

        return make_response(new_baked_good.to_dict(), 201)


@app.route("/baked_goods/<int:id>", methods=["GET", "DELETE"])
def baked_good_by_id(id):
    baked_good = BakedGood.query.filter(BakedGood.id == id).first()

    if baked_good is None:
        return make_response({"message": "Baked good not found"}, 404)

    # GET one baked good
    if request.method == "GET":
        return make_response(baked_good.to_dict(), 200)

    # DELETE baked good
    if request.method == "DELETE":
        db.session.delete(baked_good)
        db.session.commit()

        return make_response(
            {"delete_successful": True, "message": "Baked good deleted."},
            200
        )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
