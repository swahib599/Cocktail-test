from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from config import db, bcrypt

likes = db.Table('likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('cocktail_id', db.Integer, db.ForeignKey('cocktails.id'), primary_key=True)
)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    reviews = db.relationship('Review', back_populates='user')
    liked_cocktails = db.relationship('Cocktail', secondary=likes, back_populates='likes')

    serialize_rules = ('-password_hash', '-reviews.user', '-liked_cocktails.likes')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email address")
        return email

class Cocktail(db.Model, SerializerMixin):
    __tablename__ = 'cocktails'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    glass_type = db.Column(db.String(50))
    reviews = db.relationship('Review', back_populates='cocktail')
    ingredients = db.relationship('CocktailIngredient', back_populates='cocktail')
    likes = db.relationship('User', secondary=likes, back_populates='liked_cocktails')

    serialize_rules = ('-reviews.cocktail', '-ingredients.cocktail', '-likes.liked_cocktails')

class Ingredient(db.Model, SerializerMixin):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    cocktails = db.relationship('CocktailIngredient', back_populates='ingredient')

    serialize_rules = ('-cocktails.ingredient',)

class CocktailIngredient(db.Model, SerializerMixin):
    __tablename__ = 'cocktail_ingredients'

    id = db.Column(db.Integer, primary_key=True)
    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    amount = db.Column(db.String(50))
    cocktail = db.relationship('Cocktail', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='cocktails')

    serialize_rules = ('-cocktail.ingredients', '-ingredient.cocktails')

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id'), nullable=False)
    user = db.relationship('User', back_populates='reviews')
    cocktail = db.relationship('Cocktail', back_populates='reviews')

    serialize_rules = ('-user.reviews', '-cocktail.reviews')

    @validates('rating')
    def validate_rating(self, key, rating):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return rating