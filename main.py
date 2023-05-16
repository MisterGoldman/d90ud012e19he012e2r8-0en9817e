# main.py
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session, abort, make_response
from site_generator import SiteGenerator
from site_saver import SiteSaver
from user_auth import UserAuth,  db, login_manager
from file_manager import FileManager
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
from config import Config
from selenium import webdriver
import time
from download_site import DownloadSite
from site_packaging import SitePackaging


	
# New import for site preview
from site_preview import SitePreview

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

site_generator = SiteGenerator()
site_saver = SiteSaver()
user_auth = UserAuth()
file_manager = FileManager()
site_preview = SitePreview()  # New instance for site preview

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

# Setup Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless") # Ensure GUI is off
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Choose the browser (you may want to use webdriver.Firefox())
driver = webdriver.Chrome('/path/to/chromedriver', options=options)

# download site
download_site = DownloadSite(site_packaging)


with app.app_context():
    db.create_all()
	
@app.route('/preview/<template_name>/<text>/<category>', methods=['GET'])
def preview(template_name, text, category):
    # Generate the site here
    site = site_generator.generate(template_name, text, category)

    # Save it to a static HTML file (you might want to use a unique filename)
    with open('preview.html', 'w') as f:
        f.write(site)

    # Let Selenium browse to the file
    driver.get('file://' + os.path.realpath('preview.html'))

    # Give it a moment to load
    time.sleep(2)

    # Take screenshot
    driver.save_screenshot('screenshot.png')

    # Return screenshot
    return send_file('screenshot.png', mimetype='image/png')

# Don't forget to quit the driver when you're done
@app.teardown_appcontext
def quit_driver(exception=None):
    driver.quit()

# New route handler for site preview
@app.route('/preview_site', methods=['POST'])
def preview_site():
    template = request.form.get('template')
    text = request.form.get('text')
    category = request.form.get('category')
    preview_image = site_preview.preview(template, text, category)
	return render_template('preview_site.html', preview_image=preview_image)

#В этом коде мы добавили новый экземпляр `SitePreview`, который будет использоваться для #генерации предварительного просмотра веб-сайта. В обработчике маршрута для #`'/preview_site'` мы получаем необходимые данные из формы, генерируем предварительный #просмотр с помощью `site_preview.preview()`, а затем передаем полученное изображение в #шаблон `preview_site.html`.

#Пожалуйста, убедитесь, что вы обновили пути к `chromedriver` в соответствии с вашей #системой и добавили страницу `preview_site.html` в папку с шаблонами.

#Обратите внимание, что для работы этого кода вам потребуется библиотека Selenium и #драйвер браузера (например, ChromeDriver для Google Chrome). Вам нужно установить эти #зависимости, если у вас их еще нет.

#Установка Selenium:
#```sh
#pip install selenium
#https://sites.google.com/a/chromium.org/chromedriver/

@app.route('/download/<template_name>/<text>/<category>', methods=['GET'])
def download_file(template_name, text, category):
    # Получаем имя файла zip-архива
    package = download_site.download(template_name, text, category)
    response = make_response(send_file(package))
    # Добавляем заголовок для указания имени файла при скачивании
    response.headers["Content-Disposition"] = f"attachment; filename={package}"
    return response

@login_manager.user_loader
def load_user(session_token):
    user_id = ts.loads(session_token)
    user = User.query.get(user_id)

    if user is not None:
        if user.session_token == session_token:
            return user

    return None

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # TODO: Добавить валидацию данных
        # TODO: Добавить поддержку загрузки пользовательского контента (изображения, видео)
        username = request.form.get('username')
        password = request.form.get('password')
        if not user_auth.authenticate(username, password):
            # TODO: Отправить сообщение об ошибке
            pass

        category = request.form.get('category')
        template = request.form.get('template')
        text = request.form.get('text')
        site = site_generator.generate_site(category, template, text)
        zip_file = site_saver.save(site, category)
        
        # TODO: Обеспечить возможность скачивания файла пользователем
        return send_file(zip_file, as_attachment=True)
        
    # TODO: Обеспечить интерактивный выбор шаблонов
    # TODO: Обеспечить выбор нескольких шаблонов
    # TODO: Обеспечить поддержку пользовательских стилей
    # TODO: Добавить международную поддержку и локализацию
    return render_template('home.html')

if __name__ == '__main__':
    # TODO: Подумать над системой логирования
    # TODO: Подумать над системой мониторинга
    # TODO: Добавить поддержку масштабирования и балансировки нагрузки
    app.run(debug=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # TODO: Добавить валидацию данных
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        user = User(username=username, email=email, password=password)
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))  # TODO: Изменить на страницу пользователя
        except IntegrityError:
            db.session.rollback()
            # TODO: Отправить сообщение об ошибке (например, имя пользователя или электронная почта уже существуют)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: Добавить валидацию данных
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)

            # Создаем новую сессию для пользователя
            session_token = generate_password_hash(str(datetime.utcnow()), method='sha256')
            user_session = UserSession(user_id=user.id, session_token=session_token)
            db.session.add(user_session)
            db.session.commit()
            # Сохраняем токен сессии в cookies
            session['session_token'] = session_token

            return redirect(url_for('home'))  # TODO: Изменить на страницу пользователя
        # TODO: Добавить сообщение об ошибке
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Удаляем текущую сессию пользователя
    user_session = UserSession.query.filter_by(user_id=current_user.id, session_token=session.get('session_token')).first()
    if user_session:
        db.session.delete(user_session)
        db.session.commit()
    logout_user()
    return redirect(url_for('home'))

@app.before_request
def check_session():
    # Если пользователь аутентифицирован
    if current_user.is_authenticated:
        # Проверяем, есть ли у пользователя активная сессия с данным токеном
        user_session = UserSession.query.filter_by(user_id=current_user.id, session_token=session.get('session_token')).first()
        if not user_session:
            # Если нет, выходим
            logout_user()
            return redirect(url_for('login')

# Обновление функции загрузки файла
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        if file.filename == '':
            # TODO: обработать случай, когда имя файла отсутствует
            pass
        if file and photos.file_allowed(file, file.filename):
            filename = photos.save(file)
            # TODO: сохранить информацию о файле в базе данных
            return redirect(url_for('manage_files'))
        else:
            # TODO: обработать случай, когда файл не проходит проверку на допустимость
            pass
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # TODO: обработать использование загруженного файла
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # TODO: Добавить проверку на авторизацию и права доступа к файлу
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# Обновление функции управления файлами
@app.route('/manage-files', methods=['GET', 'POST'])
@login_required
def manage_files():
    # TODO: Добавить логику для отображения списка файлов
    if request.method == 'POST':
        # TODO: Добавить обработку удаления файлов
        filename = request.form.get('filename')
        file_manager.delete_file(filename)
        return redirect(url_for('manage_files'))
    return render_template('manage_files.html')

# Добавление функции удаления файла
@app.route('/delete-file/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    # TODO: Добавить проверку на права доступа к файлу
    file_manager.delete_file(filename)
    return redirect(url_for('manage_files'))

# Маршрут загрузки изображения
@app.route('/upload-image', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        # TODO: Добавить валидацию данных
        image = request.files.get('image')
        if image and photos.file_allowed(image, image.filename):
            filename = photos.save(image)
            # TODO: Сохранить информацию о файле в базе данных
            return redirect(url_for('manage_files'))
        else:
            # TODO: обработать случай, когда файл не проходит проверку на допустимость
            pass
    return render_template('upload_image.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # TODO: Добавить валидацию данных
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        if request.form.get('password'):
            current_user.password = generate_password_hash(request.form.get('password'))
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    if current_user.role != "administrator":
        abort(403)
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            user.active_until = datetime.utcnow() + timedelta(days=request.form.get('days'))
            db.session.commit()
    users = User.query.all()
    return render_template('admin.html', users=users)

#проверка подписки
@app.before_request
def check_subscription():
    if current_user.is_authenticated and current_user.active_until < datetime.utcnow():
        logout_user()

#admin panel
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    # Только администратор может получить доступ к этой странице
    if current_user.role != 'administrator':
        abort(403)
    # Здесь вы можете добавить код для отображения информации, которую вы хотите видеть в панели администратора
    return render_template('admin_dashboard.html')

#Обработка ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == "__main__":
    app.run(debug=True)
	
# import logging
# from logging.handlers import RotatingFileHandler

# Настройка логирования
# handler = RotatingFileHandler('myapp.log', maxBytes=100000, backupCount=1)
# handler.setLevel(logging.INFO)
# app.logger.addHandler(handler)
