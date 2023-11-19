# how to check for numbers https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
# how to use post and get https://pythonbasics.org/flask-http-methods/
# how to use standard html https://stackoverflow.com/a/42791810
from flask import Flask, render_template, redirect, request, session
from mongo_db import account_create, cart_add, login_checker, username_checker, cart_get_items, item_get_price, item_get_count, cart_sold, cart_remove, empty_cart, item_create, item_delete, item_update, get_menu_items, get_orders, order_create, item_find
from flask_session import Session
from datetime import datetime

app = Flask(__name__, 
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.secret_key = 'a_secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

attempts = 0

#home page
@app.route('/')
def index():
    return render_template('index.html')

#menu page
@app.route('/menu', methods=["GET", "POST"])
def menu():
    # get current menu items for each category to be rendered in menu.html
    drink_items=get_menu_items('drink')
    food_items=get_menu_items('food')
    bean_items=get_menu_items('bean')
    merch_items=get_menu_items('merch')

    return render_template('menu.html', drink_items=drink_items, food_items=food_items, bean_items=bean_items, merch_items=merch_items)

@app.route('/my_cart_add', methods=["GET", "POST"])
def my_cart_add():
    try:
        if request.method == "POST":
            if(session["name"]):
                # Retrieve the product ID from the submitted form
                product_id = request.form.get('product_id')
                username = session["name"]

                # add product to user's cart
                cart_add(username, product_id)
                return redirect('/menu')
        return redirect('/login')
    except:
        return redirect('/login')

#cart page
@app.route('/my_cart', methods=["GET", "POST"])
def my_cart():
    try:
        if(session["name"]):
            cart_items = cart_get_items(session["name"])
            item_prices = []
            total = 0.0

            # calculate total cost of cart items
            for item in cart_items:
                total += item_get_price(item) * cart_items[item]
                item_prices.append(item_get_price(item))
            total_rounded = round(total, 2)
            
            return render_template('my_cart.html', cart_items=cart_items, item_prices=item_prices, cart_price=total_rounded)
        return redirect('/login')
    except:
        return redirect('/login')


@app.route('/my_cart_remove', methods=["GET", "POST"])
def my_cart_remove():
    username = session["name"]
    item = request.form.get('item_name')

    # remove item from current user's cart
    cart_remove(username, item)
    return my_cart()

@app.route('/place_order', methods=["GET", "POST"])
def place_order():
    cart_items = cart_get_items(session["name"])

    # check if cart is empty in case of page refresh, prevents duplicate submissions
    if cart_items:
        total = 0.0

        # calculate cart total & update each item's inventory
        for item in cart_items:
            total += item_get_price(item) * cart_items[item]
            cart_sold(item, cart_items[item])
        total_rounded = round(total, 2)

        # get timestamp & add order to order_collection
        current_time = datetime.now()
        timestamp = current_time.strftime("%m/%d/%Y, %H:%M:%S")
        order_create(session["name"], cart_items, total_rounded, timestamp)

        # reset cart to empty
        empty_cart(session["name"])

        return render_template('order_submit.html', output="Order Placed!")
    else:
        return render_template('order_submit.html', output="Order Placed!")

#admin page
@app.route('/admin', methods=["GET", "POST"])
def admin_page():
    try:
        if session["name"] == 'admin':
            # get all past orders to render in admin.html
            orders_list = get_orders()
            return render_template('admin.html', orders_list=orders_list)
        return redirect('/login')
    except:
        return redirect('/login')

@app.route('/new_item', methods=["GET", "POST"])
def new_item():
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price'))
    count = int(request.form.get('count'))
    image = request.form.get('image')
    output = ""

    if name != item_find(name):
        # add item to database
        item_create(name, category, price, count, image)
        return render_template('admin.html')
    else:
        print("failed")
        return render_template('admin.html', output="Item already exists")

@app.route('/delete_item', methods=["GET", "POST"])
def delete_item():
    name = request.form.get('name')

    # delete item from database
    item_delete(name)
    return render_template('admin.html')

@app.route('/update_item', methods=["GET", "POST"])
def update_item():
    name = request.form.get('name')
    count = int(request.form.get('count'))

    # update item count
    item_update(name, count)
    return render_template('admin.html')

#about page
@app.route('/about')
def about():
    return render_template('about.html')

#login page
# flask session: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/#
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_login = request.form.get('login_username')
        password_login = request.form.get('login_password')

        # check if input credentials match a stored account
        check_user = login_checker(username_login, password_login)
        if check_user:
            session["name"] = username_login
            return render_template('login.html')
        else:
            return render_template('login.html')
    
    else:
        return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    # reset session name to None
    session["name"] = None
    return render_template('login.html')

# register
@app.route('/register')
def register():
    charactersrq = "*Password must be 8 or more characters."
    numbers = "*Password must end in a number."
    upper = "*Password must contain uppercased character."
    lower = "*Password must contain lowercased character."
    usernameRQ = "*Username must be 5 or more characters."
    unique_user = "*Username must be unique."

    return render_template('register.html', 
                            output="Password Requirements", 
                            charactersrq=charactersrq, 
                            numbers=numbers, 
                            lower=lower, 
                            upper=upper,
                            output2="Username Requirments",
                            usernameRQ=usernameRQ,
                            unique_user=unique_user)

# register checker
@app.route('/register_pass_fail', methods=["POST"])
def register_pass_fail():
    global attempts
    username = request.form.get('username')
    password = request.form.get('password')
    charactersrq = ""
    numbers = ""
    upper = ""
    lower = ""
    matched_username = ""
    usernameRQ = ""
    passed = True

    # check if username is taken
    if request.method == "POST":
        username = request.form.get('username')
        checker_user = username_checker(username)
        if checker_user:
            passed = False
            matched_username = "*Username already in use"
        else:
            passed = True
    
    # check password requirements
    if len(username) < 5:
        passed = False
        usernameRQ = "*Username must be 5 or more characters."
    if len(password) < 8:
        passed = False
        charactersrq = "*Password must be 8 or more characters."
    if not any(char.isdigit() for char in password[-1:]):
        passed = False
        numbers = "*Password must end in a number."
    if not any(char.isupper() for char in password):
        passed = False
        upper = "*Password must contain uppercased character."
    if not any(char.islower() for char in password):
        passed = False
        lower = "*Password must contain lowercased character."
    if passed:
        account_create(username,password)
        return render_template('successful.html', output="Account Creation Successful!")
    else:
        attempts += 1
        if attempts < 3:
            return render_template('register.html', 
                                   output="Registration failed these requirements try again", 
                                   charactersrq=charactersrq, 
                                   numbers=numbers, 
                                   lower=lower, 
                                   upper=upper,
                                   usernameRQ=usernameRQ,
                                   matched_username=matched_username)  
        # 3 failed attempts to lockout registration spam
        elif attempts >= 3:
            failed_attempts ="*You have made " + str(attempts) + " failed attempts!!!"
            return render_template('register.html', 
                                   output="Registration failed these requirements try again", 
                                   charactersrq=charactersrq, 
                                   numbers=numbers, 
                                   lower=lower, 
                                   upper=upper, 
                                   usernameRQ=usernameRQ,
                                   matched_username=matched_username,
                                   failed_attempt=failed_attempts)  

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
