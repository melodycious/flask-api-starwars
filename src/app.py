"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#get user

@app.route('/user', methods=['GET'])
def handle_user():

    response_body = {}
    user = User.query.all()
    response_body['results'] = [row.serialize() for row in user]
    response_body['message'] = 'Method GET User'
    return jsonify(response_body), 200

#get single user 
@app.route('/user/<int:user_id>', methods=['GET'])
def handle_single_user(user_id):

    response_body = {}
    user = User.query.get(user_id)
    response_body['results'] = [user.serialize()]
    response_body['message'] = 'Method GET User'
    return jsonify(response_body), 200

#get planets 
@app.route('/planets', methods=['GET'])
def get_planets():

    response_body = {}
    planets = Planets.query.all()
    response_body['results'] = [row.serialize() for row in planets]
    response_body['message'] = 'Method GET Planets'
    return jsonify(response_body), 200

#get single planet
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_single_planet(planets_id):

    response_body = {}
    planet = Planets.query.get(planets_id)
    if not planet:
        return jsonify('planet does not exist'), 400
    response_body['results'] = [planet.serialize()]
    response_body['message'] = 'Method GET User'
    return jsonify(response_body), 200

#get characters 
@app.route('/characters', methods=['GET'])
def get_characters():

    response_body = {}
    characters = Characters.query.all()
    response_body['results'] = [row.serialize() for row in characters]
    response_body['message'] = 'Method GET Characters'
    return jsonify(response_body), 200

#get single character 
@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_single_character(characters_id):

    response_body = {}
    character = Characters.query.get(characters_id)
    if not character:
        return jsonify('character does not exist'), 400
    response_body['results'] = [character.serialize()]
    response_body['message'] = 'Method GET User'
    return jsonify(response_body), 200

#get user favorites
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):

    response_body = {}
    user = User.query.get(user_id)
    if not user:
        return jsonify('user does not exist'), 400
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    response_body['results'] = [row.serialize() for row in favorites]
    response_body['message'] = 'method GET favorites'
    return jsonify(response_body), 200

#post favorite planet
@app.route('/user/<int:user_id>/favorites/planets/<int:planet_id>', methods = ['POST'])
def post_fav_planets_foruser(user_id, planet_id):
    
    user = User.query.get(user_id)
    if not user:
        return jsonify('user does not exist'), 400
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify('planet does not exist or other error idk'), 200
    favorite = Favorites (user_id = user_id , planet_id = planet_id)
    db.session.add(favorite)
    db.session.commit()
    response_body = {'msg':'planet added to favorites'}
    return jsonify(response_body), 200

#post favorite character
@app.route('/user/<int:user_id>/favorites/characters/<int:character_id>', methods = ['POST'])
def post_fav_character_foruser(user_id, character_id):
    
    user = User.query.get(user_id)
    if not user:
        return jsonify('user does not exist'), 400
    character = Characters.query.get(character_id)
    if not character:
        return jsonify('character does not exist or other error idk'), 200
    favorite = Favorites (user_id = user_id , character_id = character_id)
    db.session.add(favorite)
    db.session.commit()
    response_body = {'msg':'character added to favorites'}
    return jsonify(response_body), 200

#delete favorite planet
@app.route('/user/<int:user_id>/favorites/planets/<int:planet_id>', methods = ['DELETE'])
def delete_fav_planets_foruser(user_id, planet_id):
    
    favorite = Favorites.query.filter_by (user_id = user_id , planet_id = planet_id).first()
    db.session.delete(favorite)
    db.session.commit()
    response_body = {'msg':'planet deleted from favorites'}
    return jsonify(response_body), 200

#delete favorite character
@app.route('/user/<int:user_id>/favorites/characters/<int:character_id>', methods = ['DELETE'])
def delete_fav_characters_foruser(user_id, character_id):
    
    favorite = Favorites.query.filter_by (user_id = user_id , character_id = character_id).first()
    db.session.delete(favorite)
    db.session.commit()
    response_body = {'msg':'character deleted from favorites'}
    return jsonify(response_body), 200


#post planet
@app.route('/planets', methods = ['POST'])
def post_planet():

    data = request.json
    if data is None:
        return jsonify({'msg': 'please create your planet'}), 401
    if 'id' not in data or 'name' not in data or 'climate' not in data or 'diameter' not in data or 'planetDesc' not in data or 'rotation_period' not in data or 'orbital_period' not in data or 'gravity' not in data or 'population' not in data or 'terrain' not in data or 'surface_water' not in data:
        return jsonify('something went wrong, check out the data'), 400
    new_planet = Planets(
        id=data['id'],
        name=data['name'],
        climate=data['climate'],
        diameter=data['diameter'],
        planetDesc=data['planetDesc'],
        rotation_period=data['rotation_period'],
        orbital_period=data['orbital_period'],
        gravity=data['gravity'],
        population=data['population'],
        terrain=data['terrain'],
        surface_water=data['surface_water']
    )

    db.session.add(new_planet)
    db.session.commit()
    return jsonify({'msg': 'planet added succesfully'}), 200

#update planet
@app.route('/planets/<int:planet_id>', methods = ['PUT'])
def update_planet(planet_id): 
    data = request.json
    if not data:
        return jsonify({'error': 'something went wrong, check the data'}), 400
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'error' :'that planet does not exist'}), 400
    if 'name' in data:
        planet.name = data['name']
    if 'climate' in data:
        planet.climate = data['climate']
    if 'diameter' in data:
        planet.diameter = data['diameter']
    if 'planetDesc' in data:
        planet.planetDesc = data['planetDesc']
    if 'rotation_period' in data:
        planet.rotation_period = data['rotation_period']
    if 'orbital_period' in data:
        planet.orbital_period = data['orbital_period']
    if 'gravity' in data:
        planet.gravity = data['gravity']
    if 'population' in data:
        planet.population = data['population']
    if 'terrain' in data:
        planet.terrain = data['terrain']
    if 'surface_water' in data:
        planet.surface_water = data['surface_water']

    db.session.commit()
    return jsonify({'msg': 'Planet updated successfully'}), 200


#delete planet
@app.route('/planets/<int:planet_id>', methods = ['DELETE'])
def delete_planet(planet_id):

    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'message': 'planet not found'}), 404
    
    db.session.delete(planet)
    db.session.commit()

    return jsonify({'message': 'Planet deleted successfully'}), 200


#post character
@app.route('/characters', methods = ['POST'])
def post_character():

    data = request.json
    if data is None:
        return jsonify({'msg': 'you have to write something lmao'}), 401
    if 'id' not in data or 'name' not in data or 'birth_year' not in data or 'eye_color' not in data or 'characterDesc' not in data or 'height' not in data or 'mass' not in data or 'gender' not in data or 'hair_color' not in data or 'skin_color' not in data:
        return jsonify('something went wrong, check out the data'), 400
    new_character = Characters(
        id=data['id'],
        name=data['name'],
        birth_year=data['birth_year'],
        eye_color=data['eye_color'],
        characterDesc=data['characterDesc'],
        height=data['height'],
        mass=data['mass'],
        gender=data['gender'],
        hair_color=data['hair_color'],
        skin_color=data['skin_color'],

    )

    db.session.add(new_character)
    db.session.commit()
    return jsonify({'msg': 'character added succesfully'}), 200

#update character
@app.route('/characters/<int:character_id>', methods = ['PUT'])
def update_character(character_id): 
    data = request.json
    if not data:
        return jsonify({'error': 'something went wrong, check the data'}), 400
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({'error' :'that character does not exist'}), 400
    if 'name' in data:
        character.name = data['name']
    if 'birth_year' in data:
        character.birth_year = data['birth_year']
    if 'eye_color' in data:
        character.eye_color = data['eye_color']
    if 'characterDesc' in data:
        character.characterDesc = data['characterDesc']
    if 'height' in data:
        character.height = data['height']
    if 'mass' in data:
        character.mass = data['mass']
    if 'gender' in data:
        character.gender = data['gender']
    if 'hair_color' in data:
        character.hair_color = data['hair_color']
    if 'skin_color' in data:
        character.skin_color = data['skin_color']

    db.session.commit()
    return jsonify({'msg': 'Character updated successfully'}), 200

#delete character
@app.route('/characters/<int:character_id>', methods = ['DELETE'])
def delete_character(character_id):

    character = Characters.query.get(character_id)
    if character is None:
        return jsonify({'message': 'Character not found'}), 404
    
    db.session.delete(character)
    db.session.commit()

    return jsonify({'message': 'Character deleted successfully'}), 200


@app.route('/wipeall', methods=['GET'])
def database_wipe():
    try:
        db.reflect()
        db.drop_all()
        db.session.commit()
    except Exception as e:
        return "mec", 500
    return "ok", 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)