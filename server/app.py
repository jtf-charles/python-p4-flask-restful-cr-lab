#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from decimal import Decimal, InvalidOperation


from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get (self):
        response=[n.to_dict() for n in Plant.query.all()]

        return response
    
    def post(self):
        data = request.get_json(silent=False)  # <-- exigé par le client
        if not isinstance(data, dict):
            return {"error": "JSON body required"}, 400

        name  = data.get("name")
        image = data.get("image")
        price = data.get("price")

        # validations simples
        if not name:
            return {"error": "name is required"}, 400
        if not image:
            return {"error": "image is required"}, 400
        if price is None:
            return {"error": "price is required"}, 400

        # normaliser/valider le prix
        try:
            price = Decimal(str(price))
        except (InvalidOperation, ValueError):
            return {"error": "price must be a number"}, 400

        plant = Plant(name=name, image=image, price=price)
        db.session.add(plant)
        db.session.commit()
        return plant.to_dict(), 201
api.add_resource(Plants,'/plants')


class PlantByID(Resource):
    def get(self,id):
        response_to=Plant.query.filter_by(id=id).first()
        response = make_response(
            response_to.to_dict(),
            200,
        )
        return response
api.add_resource(PlantByID,'/plants/<int:id>')
        

if __name__ == '__main__':
    app.run(port=5000, debug=True)
