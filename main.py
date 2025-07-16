from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy import select, or_
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, uuid

from models import db, User, Product, Purchase, Message

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

app.secret_key = b'random_bytes!'
db.init_app(app)
socketio = SocketIO(app) 

def get_user_by(column, value):
    stmt = db.select(User).where(column==value)
    return db.session.execute(stmt).scalar_one_or_none()

def get_all_rows_from(Model):
    stmt = db.select(Model)
    return db.session.execute(stmt).scalars().all()


def save_image(image):
    _, ext = os.path.splitext(image.filename)
    unique_id = uuid.uuid4().hex
    image_name = unique_id+ext
    full_path = os.path.join(app.root_path, 'static/images', image_name)
    image.save(full_path)
    return image_name


def pagination(products, page):

    total_pages = len(products)//4 + (0 if len(products)%4==0 else 1)
    page = page or 1
    pos = (page-1)*4

    if page < total_pages:
        start_page = max(1, page-1)
        end_page = min(total_pages+1, page+5)
    else:
        start_page=max(1, page-5)
        end_page = page+1

    return  products[pos:pos+4], start_page, end_page, total_pages

def apply_filters(date, price, page, user=None, user_purchases=False): # filters + pagination logic
    
    stmt = db.select(Product)
    if user:
        if not user_purchases:
            stmt = stmt.where(Product.user_id==user.id).order_by(Product.sold.asc())
        else:
            stmt = stmt.join(Purchase, Purchase.product_id == Product.id).where(Purchase.user_id == user.id)

    else:
        stmt = stmt.where(Product.sold==False)

    if user_purchases:
        stmt = stmt.where(Product.sold==True)

    if price=='asc':
        stmt = stmt.order_by(Product.price.asc())
    elif price=='desc':
        stmt = stmt.order_by(Product.price.desc())

    if date=='asc':
        stmt = stmt.order_by(Product.date_created.asc()) 
    elif date=='desc':
        stmt = stmt.order_by(Product.date_created.desc()) 

    products = db.session.execute(stmt).scalars().all()
    return pagination(products, page)


def delete_old_history():
    stmt = db.select(Message).order_by(Message.date_created.desc()).offset(50)
    messages = db.session.execute(stmt).scalars().all()

    for msg in messages:
        db.session.delete(msg)

    db.session.commit()


@app.route("/", methods=['POST', 'GET'])
def main_page():
    username = session.get('username')
    user = get_user_by(User.username, username)
    return render_template('main.html', user=user)

@app.route("/login", methods=['POST', 'GET'])
def login():

    username=session.get('username')
    user = get_user_by(User.username, username)

    if request.method == 'POST':
        user = request.form['user']
        pswd = request.form['pswd']      
        
        stmt = db.select(User).where(or_(
                User.username == user,
                User.email == user
            )
        )
        user_found =  db.session.execute(stmt).scalar_one_or_none()

        if user_found:
            if check_password_hash(user_found.password, pswd):
                session['username'] = user_found.username
                return redirect(url_for('user_page', username=user_found.username))

        return render_template('login.html', error="Invalid login details")

    return render_template('login.html', user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('main_page'))

@app.route("/signup", methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        pswd = request.form['pswd']
        pswd_confirm = request.form['pswd-confirm']
       
        if get_user_by(User.username, username):
            return render_template('signup.html', error="Username was already taken!", email=email)
        
        if get_user_by(User.email, email):
            return render_template('signup.html', error="Email was already taken!", username=username)

        if pswd != pswd_confirm:
            return render_template('signup.html', error="Password does not match!", email=email, username=username)

        pswd = generate_password_hash(pswd)
        new_user = User(username=username, email=email, password=pswd)

        db.session.add(new_user)
        db.session.commit()

        session['username'] = username

        return redirect(url_for('user_page', username=username))

    return render_template('signup.html')


@app.route("/user/<username>", methods=['POST', 'GET'])
def user_page(username):
    
    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))
    
    user = get_user_by(User.username, username)

    if request.method == 'POST':

        new_username = request.form['username'] if 'username' in request.form else None
        new_email = request.form['email'] if 'email' in request.form else None
        pswd = request.form['pswd'] if 'pswd' in request.form else None
        
        if new_username and get_user_by(User.username, new_username):
            return redirect(url_for('user_page', username=username, username_exists=f"The Username {new_username} Is Already Taken"))
        elif new_username:
            user.username = new_username
            db.session.commit()
            session['username'] = new_username

        if new_email and get_user_by(User.email, new_email):
            return redirect(url_for('user_page', username=username, email_exists=f"The Email {new_email} Is Already Taken"))
        elif new_email:
            user.email = new_email
            db.session.commit()

        if pswd:
            if not check_password_hash(user.password, pswd):
                return redirect(url_for('user_page', username=username, wrong_password="The Password Was Not Correct"))
            else:
                db.session.delete(user)
                db.session.commit()
                session.clear()
                return redirect(url_for('main_page'))

        new_username = user.username
        return redirect(url_for('user_page', username=new_username))
    
    username_exists = request.args.get('username_exists')
    email_exists = request.args.get('email_exists')
    wrong_password = request.args.get('wrong_password')

    product_published = request.args.get('success')

    return render_template("user.html", 
        user=user, 
        username_exists=username_exists,
        email_exists=email_exists,
        wrong_password=wrong_password,
        product_published=product_published)


@app.route("/user/<username>/products/")
@app.route("/user/<username>/products/<int:page>")
def user_products(username, page=None):
    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))
    
    date = request.args.get('date', '')
    price = request.args.get('price', '')

    user = get_user_by(User.username, username)

    products, start_page, end_page, total_pages = apply_filters(date, price, page, user)
    page = page or 1
    if (page > total_pages and total_pages != 0):
        return redirect(url_for('view_products'));

    return render_template("all_products.html", 
        products=products, 
        user=user, 
        current_page=page, 
        start_page=start_page, 
        end_page=end_page,
        total_pages=total_pages,
        user_page=True
    )

@app.route("/user/<username>/purchases/")
@app.route("/user/<username>/purchases/<int:page>")
def user_purchases(username, page=None):
    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))
    date = request.args.get('date', '')
    price = request.args.get('price', '')

    user = get_user_by(User.username, username)
    products, start_page, end_page, total_pages = apply_filters(date, price, page, user, user_purchases=True)
    page = page or 1 
    if (page > total_pages and total_pages != 0):
        return redirect(url_for('view_products'));

    return render_template("all_products.html", 
        products=products, 
        user=user, 
        current_page=page, 
        start_page=start_page, 
        end_page=end_page,
        total_pages=total_pages,
        user_page=True
    )

@app.route("/user/<username>/publish_product", methods=['POST', 'GET']) 
def publish_product(username):

    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))
    user = get_user_by(User.username, username)
    if request.method=='POST':

        product_title=request.form['title']
        product_price=request.form['price']
        product_description=request.form['p-description'] or ""

        image = request.files['ProductImage']
        if image and image.filename != '':
            image_name = save_image(image)
        else:
            image_name = 'default.jpg'
        
        foreign_key =  get_user_by(User.username, username).id
        product = Product(title=product_title, price=product_price, picture=image_name, description=product_description, user_id=foreign_key)
        
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('user_page', username=username, success=1))
    
    return render_template("publish_product.html", user=user)

@app.route("/user/<username>/update_product/<int:product_id>",  methods=['POST', 'GET'])
def update_product(username, product_id):

    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))
    user = get_user_by(User.username, username)
    product = db.session.get(Product, product_id)
    if product and product.seller.username == username:
        if request.method=='POST':
            product_title=request.form['title']
            product_price=request.form['price']
            product_description=request.form['p-description'] or ""

            image = request.files['ProductImage']
            if image and image.filename != '':
                image_name = save_image(image)
            else:
                if 'remove_picture' in request.form:
                    image_name='default.jpg'
                else:
                    image_name = product.picture

            product.title = product_title
            product.price = product_price
            product.description = product_description
            product.picture = image_name
            db.session.commit()

            return redirect(url_for('view_product', product_id=product.id)) 
        
        return render_template("publish_product.html", user=user,product=product) # On page load if product id exists (GET request)

    return redirect(url_for('user_products', username=username)) # On page load if product id does not exist (GET request)

@app.route("/user/<username>/delete_post/<int:product_id>")
def delete_product(username, product_id):
    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))
    product = db.session.get(Product, product_id)
    if product and product.seller.username == username:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('user_products', username=username))

@app.route("/products/")
@app.route("/products/<int:page>")
def view_products(page=None):

    current_username = session.get('username')

    date = request.args.get('date', '')
    price = request.args.get('price', '')
    user = get_user_by(User.username, current_username)

    products, start_page, end_page, total_pages = apply_filters(date, price, page)
    page = page or 1
    
    if (page > total_pages and total_pages != 0):
        return redirect(url_for('view_products'));
  
    return render_template("all_products.html", 
        products=products, 
        user=user, 
        current_page=page, 
        start_page=start_page, 
        end_page=end_page,
        total_pages=total_pages
    )

@app.route("/product/<int:product_id>")
def view_product(product_id):

    product = db.session.get(Product, product_id)
    current_username = session.get('username')
    user = get_user_by(User.username, current_username)
    if not product:
        return redirect(url_for('view_products'))
    
    return render_template('product.html', user=user, product=product)


@app.route("/user/<username>/buy_product/<int:product_id>")
def buy_product(username, product_id):
    if 'username' not in session or session.get('username') != username or not get_user_by(User.username, session.get('username')):
        return redirect(url_for('login'))

    product = db.session.get(Product, product_id)
    user = get_user_by(User.username, username)

    if product and product.user_id != user.id:
        
        if user.balance >= product.price:

            product.sold = True
            user.balance -= product.price
            user.spent += product.price
            seller = db.session.get(User, product.user_id)
            seller.balance += product.price
            seller.earned += product.price
            purchased_product = Purchase(product_id=product.id, user_id=user.id)

            db.session.add(purchased_product)
            db.session.commit()

            return  redirect(url_for('view_products', success=1))
        else:   
            return render_template("product.html", product=product, user=user, error_message="Insufficient Funds!")
    
    return redirect(url_for('view_products')) 


@app.route("/chat")
def chat():

    stmt = db.select(Message).order_by(Message.date_created.desc()).limit(50)
    messages = db.session.execute(stmt).scalars().all()

    username = session.get('username')
    user = get_user_by(User.username, username)

    return render_template('chat.html', messages=reversed(messages), user=user)


@app.route("/about")
def about():
    return render_template('about.html')

@socketio.on("receive_message")
def receive_message(data):

    message = data["content"]
    
    username = session.get('username')
    user = get_user_by(User.username, username)

    new_message = Message(message=message, user_id=user.id)
    db.session.add(new_message)
    db.session.commit()

    delete_old_history()
    emit("send_message", {
        "user": username,
        "content": message,
        "timestamp": new_message.date_created.isoformat()
    }, broadcast=True)


if __name__=="__main__":
    with app.app_context():   # Needed for DB operations
        db.create_all()      # Creates the database and tables
    #socketio.run(app, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) # connect from different devices on your network using http://ipv4:5000
   