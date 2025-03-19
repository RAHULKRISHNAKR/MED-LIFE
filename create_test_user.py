from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if test user already exists
    if not User.query.filter_by(email="test@example.com").first():
        # Create a test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
        print("Email: test@example.com")
        print("Password: password123")
    else:
        print("Test user already exists!")
        print("Email: test@example.com")
        print("Password: password123")
