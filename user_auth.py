# user_auth.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



        # TODO: Добавить отправку подтверждающего письма при регистрации (добавить дополнительную проверку перед отправкой письма, капча + проверка на валидность емейла( что это действительно емейл а не sql иньекция ( то есть что бы меня не взломали))
		# TODO: Добавить поддержку более сложную проверку пользователей (нужно максимально защититься от взлома или стороннего вмешательства, а так же сделать НЕ возможным перебор(брут) паролей)
        # TODO: Добавить поддержку более сложных методов аутентификации ( мы реализовывали это через в модуле password_auth.py через google authenticator, главое удостоверься что бы это работало)
        # TODO: Добавить шифрование паролей (достаточно просто добавить нестандартную соль (Salt) 
		# TODO: добавить капчу на вход, забыл пароль, регистрация.
		# TODO: Добавить поддержку сессий и куки ( 1 пользователь = 1 сессия, если авторизовывается во второй то первая разлогинивается с сообщением вы авторизовались в другом месте)