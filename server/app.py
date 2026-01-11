from models import db, Hero, Power, HeroPower
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([
        hero.to_dict(only=("id", "name", "super_name"))
        for hero in heroes
    ]), 200
    
@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero(id):
    hero = Hero.query.get(id)

    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    return jsonify(
        hero.to_dict(
            only=("id", "name", "super_name"),
            include={
                "hero_powers": {
                    "only": ("id", "hero_id", "power_id", "strength"),
                    "include": {
                        "power": {
                            "only": ("id", "name", "description")
                        }
                    }
                }
            }
        )
    ), 200
    
@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    return jsonify([
        power.to_dict(only=("id", "name", "description"))
        for power in powers
    ]), 200
    
@app.route("/powers/<int:id>", methods=["GET"])
def get_power(id):
    power = Power.query.get(id)

    if not power:
        return jsonify({"error": "Power not found"}), 404

    return jsonify(
        power.to_dict(only=("id", "name", "description"))
    ), 200
        
@app.route("/powers/<int:id>", methods=["PATCH"])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()

    try:
        power.description = data.get("description", power.description)

        db.session.commit()
        return jsonify({
            "id": power.id,
            "name": power.name,
            "description": power.description
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({
            "errors": [str(e)]
        }), 400
    
@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json()

    try:
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"]
        )

        db.session.add(hero_power)
        db.session.commit()

        return jsonify(
            hero_power.to_dict(
                only=("id", "hero_id", "power_id", "strength"),
                include={
                    "hero": {
                        "only": ("id", "name", "super_name")
                    },
                    "power": {
                        "only": ("id", "name", "description")
                    }
                }
            )
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errors": ["validation errors"]
        }), 400