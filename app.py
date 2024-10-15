from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, User, Cocktail, Ingredient, CocktailIngredient, Review
from config import Config
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app, supports_credentials=True)
Session(app)

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            return {'message': 'Logged in successfully'}, 200
        return {'message': 'Invalid credentials'}, 401

class UserLogout(Resource):
    def post(self):
        session.pop('user_id', None)
        return {'message': 'Logged out successfully'}, 200

class CocktailList(Resource):
    def get(self):
        cocktails = Cocktail.query.all()
        return jsonify([cocktail.to_dict() for cocktail in cocktails])

    def post(self):
        if 'user_id' not in session:
            return {'message': 'Unauthorized'}, 401
        data = request.get_json()
        new_cocktail = Cocktail(name=data['name'], instructions=data['instructions'], image_url=data['image_url'])
        db.session.add(new_cocktail)
        db.session.commit()
        return new_cocktail.to_dict(), 201

class CocktailResource(Resource):
    def get(self, id):
        cocktail = Cocktail.query.get_or_404(id)
        return cocktail.to_dict()

    def patch(self, id):
        if 'user_id' not in session:
            return {'message': 'Unauthorized'}, 401
        cocktail = Cocktail.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items():
            setattr(cocktail, key, value)
        db.session.commit()
        return cocktail.to_dict()

    def delete(self, id):
        if 'user_id' not in session:
            return {'message': 'Unauthorized'}, 401
        cocktail = Cocktail.query.get_or_404(id)
        db.session.delete(cocktail)
        db.session.commit()
        return '', 204

class ReviewList(Resource):
    def get(self):
        reviews = Review.query.all()
        return jsonify([review.to_dict() for review in reviews])

    def post(self):
        if 'user_id' not in session:
            return {'message': 'Unauthorized'}, 401
        data = request.get_json()
        new_review = Review(content=data['content'], rating=data['rating'], user_id=session['user_id'], cocktail_id=data['cocktail_id'])
        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict(), 201

api.add_resource(UserRegister, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogout, '/api/logout')
api.add_resource(CocktailList, '/api/cocktails')
api.add_resource(CocktailResource, '/api/cocktails/<int:id>')
api.add_resource(ReviewList, '/api/reviews')

if __name__ == '__main__':
    app.run(port=5555, debug=True)