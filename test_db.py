from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    # Attempt to create
    print('creating user')
    User.create('testuser99', 'test99@example.com', 'mypassword')
    
    # Attempt to retrieve
    print('retrieving user')
    u = User.get_by_email('test99@example.com')
    if u:
        print('User found:', u.email)
        print('Hash check:', u.check_password('mypassword'))
    else:
        print('User not found')
