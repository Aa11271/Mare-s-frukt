# routes.py
from flask import abort, render_template, request, url_for, flash, redirect
from .forms import RegistrationForm, LoginForm, StorageForm
from .models import User, Storage, get_main_storage_data
from .extensions import db, bcrypt, cache
from flask_login import login_user, current_user, logout_user, login_required



def configure_routes(app):

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Izlogovani ste!', 'success')
        return redirect(url_for('home'))
    
    @app.route('/storage/new', methods=['GET', 'POST'])
    @login_required
    def new_storage():
     form = StorageForm()
     if form.validate_on_submit():
        storage_type = request.form.get('storage_type')
        if storage_type == 'small':
            # Logic to create small storage
            flash('Small storage created!', 'success')
        elif storage_type == 'central':
            # Logic to create central storage
            flash('Central storage created!', 'success')
        # Assuming the Storage model has a 'name' field and a foreign key 'user_id'
        storage = Storage(name=form.name.data, user_id=current_user.id)
        db.session.add(storage)
        db.session.commit()
        return redirect(url_for('view_storages'))  # Adjust to the correct route
     return render_template('create_storage.html', form=form)

    @app.route('/main_storage')
    @login_required
    @cache.cached(timeout=300)  # Cache this view for 5 minutes
    def main_storage():
     storage_items = Storage.query.filter_by(user_id=current_user.id).all()
     return render_template('main_storage.html', storage_items=storage_items)
    
    @cache.cached(timeout=300, key_prefix='main_storage_data')
    def get_main_storage_data_cached():
     # This function will be cached, so it only retrieves data from the database
     # if the cache has expired or is empty
     return get_main_storage_data()
    
    @app.route('/storages')
    @login_required
    def view_storages():
     storages = Storage.query.filter_by(user_id=current_user.id).all()
     return render_template('view_storage.html', storages=storages)

    @app.errorhandler(403)
    def forbidden(e):
     return render_template('403.html'), 403  # Ensure you have a 403.html template

    @app.route('/edit_storage/<int:storage_id>', methods=['GET', 'POST'])
    def edit_storage(storage_id):
     storage = Storage.query.get_or_404(storage_id)
     if request.method == 'POST':
        # Assuming there's a form to process the edit
        form = StorageForm(request.form)
        if form.validate_on_submit():
            # Process the validated form data and update storage
            storage.name = form.name.data
            # ... other fields
            db.session.commit()
            flash('Storage updated successfully!', 'success')
            return redirect(url_for('view_storages', storage_id=storage.id))
        else:
            # Form didn't validate, fall through to the render_template call
            flash('Error updating storage.', 'error')
            # GET request or failed POST validation: render the edit page
     form = StorageForm(obj=storage)
     return render_template('edit_storage.html', form=form, storage_id=storage_id)

    @app.route('/delete_storage/<int:storage_id>')
    @login_required
    def delete_storage(storage_id):
     storage = Storage.query.get_or_404(storage_id)
     if storage.user_id != current_user.id:
        abort(403)  # HTTP Forbidden status code
     db.session.delete(storage)
     db.session.commit()
     flash('Storage deleted successfully', 'success')
     return redirect(url_for('view_storages'))
