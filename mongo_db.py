# intal code given from mongodb https://www.mongodb.com/docs/drivers/pymongo/
# mongodb tutorial https://www.geeksforgeeks.org/mongodb-python-insert-update-data/#
# mongodb video https://www.youtube.com/watch?v=3wNvKybVyaI&ab_channel=NeuralNine
from pymongo import MongoClient
uri = "mongodb://localhost:27017"
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# database
db = client.user_accounts

# collections
user_collection = db.users
item_collection = db.items
order_collection = db.orders

# ADMIN FUNCTIONS
def item_create(name, category, price, count, image):
    # structure of items in item_collection
    newItem = {
        'name': name,
        'category': category,
        'price': price,
        'count': count,
        'image': image
    }
    item_collection.insert_one(newItem)

def item_delete(name):
    myString = "items."
    myString += name

    # delete the item from all user accounts where it exists
    user_collection.update_many({myString: {"$exists": True}}, {"$unset": {myString: 1}})

    # delete item from item_collection
    item_collection.delete_one({'name':name})
    return item_collection

def item_update(name, count):
    # change inventory count of the given item
    item_collection.update_one({'name':name}, {'$set': {'count':count}})
    return item_collection

def item_find(name):
    # helper function to find item by name
    item = item_collection.find_one({'name':name})
    if item:
        return item['name']
    else:
        return "fail"

def order_create(user, itemdict, total, timestamp):
    # track order numbers
    num = len(get_orders()) + 1

    # structure of orders in order_collection
    newOrder = {
        'num': num,
        'user': user,
        'itemdict': itemdict,
        'total': total,
        'timestamp': timestamp
    }
    order_collection.insert_one(newOrder)

def get_orders():
    orders_list = []
    orders = order_collection.find()

    # set structure of orders for admin page
    for order in orders:
        orders_list.append({
            'num': order['num'],
            'user': order['user'],
            'itemdict': order['itemdict'],
            'total': order['total'],
            'timestamp': order['timestamp']
        })

    return orders_list

# MENU FUNCTIONS
def get_menu_items(category):
    menu_items = []
    items = item_collection.find({'category':category})

    # set structure of items for menu page
    for item in items:
        menu_items.append({
            'item_name': item['name'],
            'item_category': item['category'],
            'item_price': item['price'],
            'item_count': item['count'],
            'item_image': item['image']
        })

    return menu_items


# CART FUNCTIONS
def cart_get_items(username):
    cart_items_raw = user_collection.find_one({'username':username}, {'items'})
    cart_items = cart_items_raw['items']

    # item stock check
    for item in cart_items:
        count = item_get_count(item)
        myString = "items."
        myString += item

        # if item is out of stock, remove it from cart
        if count <= 0:
            user_collection.update_one({'username':username}, {'$unset': {myString: 0}})
        # if the quantity of an item in the cart is higher than the item's inventory count, set quantity to inventory count; max out cart quantitity at inventory count
        if count < cart_items[item]:
            user_collection.update_one({'username':username}, {'$set': {myString: count}})
    
    # refresh cart_items after item stock check
    cart_items_raw = user_collection.find_one({'username':username}, {'items'})
    
    return cart_items_raw['items']

def item_get_price(name):
    # helper function to get price of an item
    price = item_collection.find_one({'name':name}, {'price'})
    return price['price']

def item_get_count(name):
    # helper function to get current count of an item
    count = item_collection.find_one({'name':name}, {'count'})
    return count['count']

def cart_add(username, item):
    # appending the item variable to "items." allows accessing elements of the nested dictionary in a user file
    myString = "items."
    myString += item

    if user_collection.find_one({'username':username}, {myString}):
        user_collection.update_one({'username':username}, {'$inc': {myString: 1}})
    else:
        user_collection.update_one({'username':username}, {'$set': {myString: 1}})
    return user_collection

def cart_remove(username, item):
    myString = "items."
    myString += item

    # since the items dict is nested, it is easier to rewrite the dict and pop the chosen item...
    items = user_collection.find_one({'username':username}, {'items'})
    new_items = items['items']
    new_items.pop(item)

    # ...then replace the old items dict with the new one
    user_collection.update_one({'username':username}, {'$set': {'items': new_items}})
    return user_collection

def cart_sold(name, quantity):
    # update item count for sold item
    item_collection.update_one({'name':name}, {'$inc': {'count':-quantity}})
    return item_collection

def empty_cart(username):
    # reset user cart to empty
    user_collection.update_one({'username':username}, {'$set': {'items':{}}})

# ACCOUNT FUNCTIONS
def account_create(username, password):
    # user account structure in user_collection
    user = {
        'username': username,
        'password': password,
        'items': {}
    }
    user_collection.insert_one(user)

def login_checker(username, password):
    # how to use find_one https://www.geeksforgeeks.org/python-mongodb-find_one-query/#
    user_creds = user_collection.find_one({'username': username, 'password': password})
    #user_id = user_creds["_id"]
    if user_creds:
        return True
    else:
        return False

def username_checker(username):
    # check for taken username
    username_finder = user_collection.find_one({'username': username})
    if username_finder:
        return True
    else:
        return False
