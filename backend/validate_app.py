from app import create_app, db
from app.models import Role

app = create_app('testing')
with app.app_context():
    db.create_all()
    print('DB OK')
    print('roles', Role.query.all())
