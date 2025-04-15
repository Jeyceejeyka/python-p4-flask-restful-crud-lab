#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource # type: ignore

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

with app.app_context():
    db.create_all()  # Ensure tables are created

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'image', 'price']
        if not all(field in data for field in required_fields):
            return {'error': 'Missing required fields'}, 400

        try:
            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=float(data['price']),
            )

            db.session.add(new_plant)
            db.session.commit()

            return make_response(new_plant.to_dict(), 201)
        except ValueError:
            return {'error': 'Invalid price format'}, 400


api.add_resource(Plants, '/plants')


class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return {"error": "Plant not found"}, 404  # Return 404 if plant is not found
        return plant.to_dict(), 200

    def patch(self, id):
        data = request.get_json()

        plant = Plant.query.filter_by(id=id).first()
        if not plant:  # Handle case where plant is not found
            return make_response({"error": "Plant not found"}, 404)

        for attr in data:
            setattr(plant, attr, data[attr])

        db.session.add(plant)
        db.session.commit()

        return make_response(plant.to_dict(), 200)

    def delete(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:  # Handle case where plant is not found
            return make_response({"error": "Plant not found"}, 404)

        db.session.delete(plant)
        db.session.commit()

        return make_response('', 204)


api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)