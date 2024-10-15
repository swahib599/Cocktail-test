from app import app, db
from models import User, Cocktail, Ingredient, CocktailIngredient, Review

def seed_database():
    with app.app_context():
        print("Seeding database...")

        # Clear existing data
        db.drop_all()
        db.create_all()

        # Seed Users
        user1 = User(username="cocktail_lover", email="lover@cocktails.com")
        user1.set_password("password123")
        db.session.add(user1)

        # Seed Cocktails
        mojito = Cocktail(
            name="Mojito",
            instructions="Muddle mint leaves with sugar and lime juice. Add a splash of soda water and fill the glass with cracked ice. Pour the rum and top with soda water. Garnish with mint leaves and a lime wedge.",
            image_url="https://example.com/mojito.jpg"
        )
        db.session.add(mojito)

        margarita = Cocktail(
            name="Margarita",
            instructions="Rub the rim of the glass with the lime slice to make the salt stick to it. Shake the other ingredients with ice, then carefully pour into the glass (taking care not to dislodge any salt). Garnish and serve over ice.",
            image_url="https://example.com/margarita.jpg"
        )
        db.session.add(margarita)

        # Seed Ingredients
        rum = Ingredient(name="White rum")
        tequila = Ingredient(name="Tequila")
        lime_juice = Ingredient(name="Lime juice")
        sugar = Ingredient(name="Sugar")
        mint = Ingredient(name="Mint leaves")
        salt = Ingredient(name="Salt")
        db.session.add_all([rum, tequila, lime_juice, sugar, mint, salt])

        # Seed CocktailIngredients
        mojito_rum = CocktailIngredient(cocktail=mojito, ingredient=rum, amount="60 ml")
        mojito_lime = CocktailIngredient(cocktail=mojito, ingredient=lime_juice, amount="30 ml")
        mojito_sugar = CocktailIngredient(cocktail=mojito, ingredient=sugar, amount="2 tsp")
        mojito_mint = CocktailIngredient(cocktail=mojito, ingredient=mint, amount="6 leaves")

        margarita_tequila = CocktailIngredient(cocktail=margarita, ingredient=tequila, amount="50 ml")
        margarita_lime = CocktailIngredient(cocktail=margarita, ingredient=lime_juice, amount="25 ml")
        margarita_salt = CocktailIngredient(cocktail=margarita, ingredient=salt, amount="1 tbsp")

        db.session.add_all([mojito_rum, mojito_lime, mojito_sugar, mojito_mint, margarita_tequila, margarita_lime, margarita_salt])

        # Seed Reviews
        mojito_review = Review(content="Perfect for a hot summer day!", rating=5, user=user1, cocktail=mojito)
        margarita_review = Review(content="Classic and delicious!", rating=4, user=user1, cocktail=margarita)
        db.session.add_all([mojito_review, margarita_review])

        db.session.commit()
        print("Database seeded!")

if __name__ == "__main__":
    seed_database()