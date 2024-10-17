from flask import Flask, request, session, jsonify, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from config import app, db
from models import User, Cocktail, Ingredient, CocktailIngredient, Review
from sqlalchemy.exc import IntegrityError
import os
from flask_session import Session

api = Api(app)
CORS(app, supports_credentials=True)

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Use only with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
Session(app)

# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# API Routes
class AuthStatus(Resource):
    def get(self):
        if 'user_id' not in session:
            return {'isAuthenticated': False, 'user': None}, 200
        user = User.query.get(session['user_id'])
        if user:
            return {'isAuthenticated': True, 'user': user.to_dict(rules=('-liked_cocktails',))}, 200
        return {'isAuthenticated': False, 'user': None}, 200

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = User(
                username=data['username'],
                email=data['email']
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(rules=('-liked_cocktails',)), 201
        except IntegrityError:
            return {'error': 'Username or email already exists'}, 422

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            return user.to_dict(rules=('-liked_cocktails',)), 200
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def post(self):
        session.pop('user_id', None)
        return '', 204

class CocktailList(Resource):
    def get(self):
        cocktails = Cocktail.query.all()
        return [cocktail.to_dict(rules=('-reviews', '-ingredients', '-likes')) for cocktail in cocktails], 200

    def post(self):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        data = request.get_json()
        new_cocktail = Cocktail(
            name=data['name'],
            instructions=data['instructions'],
            image_url=data['image_url'],
            glass_type=data.get('glass_type', '')
        )
        db.session.add(new_cocktail)
        
        for ingredient_data in data.get('ingredients', []):
            ingredient = Ingredient.query.filter_by(name=ingredient_data['name']).first()
            if not ingredient:
                ingredient = Ingredient(name=ingredient_data['name'])
                db.session.add(ingredient)
            
            cocktail_ingredient = CocktailIngredient(
                cocktail=new_cocktail,
                ingredient=ingredient,
                amount=ingredient_data.get('amount', '')
            )
            db.session.add(cocktail_ingredient)
        
        db.session.commit()
        return new_cocktail.to_dict(rules=('-reviews', '-ingredients', '-likes')), 201

class CocktailResource(Resource):
    def get(self, id):
        cocktail = Cocktail.query.get_or_404(id)
        return cocktail.to_dict(rules=('-reviews.cocktail', '-ingredients.cocktail', '-likes.liked_cocktails')), 200

    def patch(self, id):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        cocktail = Cocktail.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items():
            if key != 'ingredients':
                setattr(cocktail, key, value)
        
        if 'ingredients' in data:
            CocktailIngredient.query.filter_by(cocktail_id=cocktail.id).delete()
            
            for ingredient_data in data['ingredients']:
                ingredient = Ingredient.query.filter_by(name=ingredient_data['name']).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_data['name'])
                    db.session.add(ingredient)
                
                cocktail_ingredient = CocktailIngredient(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=ingredient_data.get('amount', '')
                )
                db.session.add(cocktail_ingredient)
        
        db.session.commit()
        return cocktail.to_dict(rules=('-reviews.cocktail', '-ingredients.cocktail', '-likes.liked_cocktails')), 200

    def delete(self, id):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        cocktail = Cocktail.query.get_or_404(id)
        db.session.delete(cocktail)
        db.session.commit()
        return '', 204

class LikeCocktail(Resource):
    def post(self, id):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        cocktail = Cocktail.query.get_or_404(id)
        user = User.query.get(session['user_id'])
        if user not in cocktail.likes:
            cocktail.likes.append(user)
            db.session.commit()
        return {'likes': len(cocktail.likes)}, 200

class UnlikeCocktail(Resource):
    def post(self, id):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        cocktail = Cocktail.query.get_or_404(id)
        user = User.query.get(session['user_id'])
        if user in cocktail.likes:
            cocktail.likes.remove(user)
            db.session.commit()
        return {'likes': len(cocktail.likes)}, 200

class ReviewList(Resource):
    def get(self, cocktail_id):
        reviews = Review.query.filter_by(cocktail_id=cocktail_id).all()
        return [review.to_dict(rules=('-user.reviews', '-cocktail')) for review in reviews], 200

    def post(self, cocktail_id):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        data = request.get_json()
        new_review = Review(
            content=data['content'],
            rating=data['rating'],
            user_id=session['user_id'],
            cocktail_id=cocktail_id
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict(rules=('-user.reviews', '-cocktail')), 201

# Add resources to API
api.add_resource(AuthStatus, '/api/auth/status')
api.add_resource(Signup, '/api/signup')
api.add_resource(Login, '/api/login')
api.add_resource(Logout, '/api/logout')
api.add_resource(CocktailList, '/api/cocktails')
api.add_resource(CocktailResource, '/api/cocktails/<int:id>')
api.add_resource(LikeCocktail, '/api/cocktails/<int:id>/like')
api.add_resource(UnlikeCocktail, '/api/cocktails/<int:id>/unlike')
api.add_resource(ReviewList, '/api/cocktails/<int:cocktail_id>/reviews')

if __name__ == '__main__':
    app.run(port=5555, debug=True)