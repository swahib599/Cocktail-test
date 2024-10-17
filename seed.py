import logging
from config import app, db
from models import User, Cocktail, Ingredient, CocktailIngredient, Review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    try:
        logger.info("Starting the seeding process...")

        # Clear existing data
        deleted = Cocktail.query.delete()
        db.session.commit()
        logger.info(f"Deleted {deleted} existing cocktails.")

        cocktails = [
            {
                "name": "Mojito",
                "id": 1,
                "image": "/static/mojito.jpeg",
                "ingredients": [
                    "2 oz White Rum",
                    "1 oz Fresh Lime Juice",
                    "2 tsp Sugar",
                    "6-8 Fresh Mint Leaves",
                    "Club Soda",
                    "Mint Sprig for garnish"
                ],
                "directions": "Muddle mint leaves and sugar with lime juice. Add rum and top with club soda. Garnish with mint sprig.",
                "glass_type": "Highball Glass"
            },
            {
                "name": "Margarita",
                "id": 2,
                "image": "/static/margarita.jpeg",
                "ingredients": [
                    "2 oz Tequila",
                    "1 oz Lime Juice",
                    "1 oz Triple Sec",
                    "Salt for rimming glass",
                    "Lime wedge for garnish"
                ],
                "directions": "Rub the rim of the glass with lime and dip in salt. Shake tequila, lime juice, and triple sec with ice. Strain into glass.",
                "glass_type": "Cocktail Glass"
            },
            # Add more cocktails here as needed
        ]

        for cocktail_data in cocktails:
            cocktail = Cocktail(
                id=cocktail_data['id'],
                name=cocktail_data['name'],
                image_url=cocktail_data['image'],
                instructions=cocktail_data['directions'],
                glass_type=cocktail_data['glass_type']
            )
            db.session.add(cocktail)
            logger.debug(f"Added cocktail: {cocktail.name}")

            # Add ingredients
            for ingredient_str in cocktail_data['ingredients']:
                parts = ingredient_str.split(' ', 1)
                amount = parts[0] if len(parts) > 1 else ''
                name = parts[1] if len(parts) > 1 else parts[0]
                
                ingredient = Ingredient.query.filter_by(name=name).first()
                if not ingredient:
                    ingredient = Ingredient(name=name)
                    db.session.add(ingredient)
                
                cocktail_ingredient = CocktailIngredient(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=amount
                )
                db.session.add(cocktail_ingredient)

        db.session.commit()
        logger.info("Cocktail data seeded successfully!")

    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while seeding data: {e}")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
        print("Cocktail data seeded successfully!")