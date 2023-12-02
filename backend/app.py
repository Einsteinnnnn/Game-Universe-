import re
import sys
from flask import Flask, request, session
from datetime import timedelta
from database import MyDatabase

app = Flask(__name__, static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = 'GameUniverse'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

if len(sys.argv) < 2:
    sys.exit('Include netid as database username. Usage: $ python app.py [netid]')
my_database = MyDatabase(username=sys.argv[1], password='123456')
if not my_database.is_connected():
    sys.exit('Failed to connect to database. Check your username and password.')


@app.errorhandler(404)
def index(e):
    return app.send_static_file('index.html')


@app.route('/api/login', methods=['POST'])
def login():
    post_data = request.get_json()
    try:
        username = post_data['username']
        password = post_data['password']
    except KeyError:
        return {'status': 'error', 'message': 'Invalid request.'}
    check = my_database.user_login(username, password)
    if check:
        uid = my_database.username_check(username)[0][0]
        session['uid'] = uid
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Invalid username or password.'}


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('uid', None)
    return {'status': 'ok'}


@app.route('/api/user', methods=['GET'])
def user_info():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    result = my_database.get_userinfo(uid)
    if result:
        return {'status': 'ok', 'data': result}
    else:
        return {'status': 'error', 'message': 'Invalid username.'}
    

@app.route('/api/register', methods=['POST'])
def register():
    post_data = request.get_json()
    try:
        username = post_data['username']
        password = post_data['password']
        email = post_data['email']
        phone = post_data['phone']
    except KeyError:
        return {'status': 'error', 'message': 'Invalid request.'}
    check = my_database.username_check(username)
    if check:
        return {'status': 'error', 'message': 'Username already exists.'}
    else:
        if my_database.user_register(username, password, email, phone):
            return {'status': 'ok'}
        else:
            return {'status': 'error', 'message': 'Failed to register.'}
        

@app.route('/api/basic-search', methods=['GET'])
def basic_search():
    keyword = request.args.get('keyword')
    if keyword:
        result = my_database.search_by_keyword(keyword)
        if result:
            return {'status': 'ok', 'data': result}
        else:
            return {'status': 'ok', 'data': []}
    else:
        return {'status': 'error', 'message': 'Invalid request.'}
    

@app.route('/api/advanced-search', methods=['POST'])
def advanced_search():
    post_data = request.get_json()
    try:
        genre = post_data['genre']
        category = post_data['category']
        os_platforms = post_data['os_platforms']
        language = post_data['language']
        required_age = post_data['required_age']
        metacritic_lowerbnd = post_data['metacritic_lowerbnd']
        steam_spy_owners = post_data['steamspyowners']
        price_lower = post_data['price'][0]*10
        price_upper = post_data['price'][1]*10
    except:
        return {'status': 'error', 'message': 'Invalid request.'}
    result = my_database.search_by_filter(genre, category, os_platforms, language, required_age, metacritic_lowerbnd, steam_spy_owners, price_lower, price_upper)
    if result:
        return {'status': 'ok', 'data': result}
    else:
        return {'status': 'ok', 'data': []}


@app.route('/api/favorite-games', methods=['GET'])
def favorite_games():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    result = my_database.get_userfavorite(uid)
    if result:
        return {'status': 'ok', 'data': result}
    else:
        return {'status': 'ok', 'data': []}
    

@app.route('/api/favorite-games-add', methods=['POST'])
def favorite_games_add():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    post_data = request.get_json()
    try:
        gameid = post_data['gameid']
    except:
        return {'status': 'error', 'message': 'Invalid request.'}
    if my_database.add_favorite(uid, gameid):
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Failed to add favorite game.'}
    

@app.route('/api/favorite-games-delete', methods=['POST'])
def favorite_games_delete():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    post_data = request.get_json()
    try:
        gameid = post_data['gameid']
    except:
        return {'status': 'error', 'message': 'Invalid request.'}
    if my_database.delete_favorite(uid, gameid):
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Failed to delete favorite game.'}
    

@app.route('/api/game-info', methods=['GET'])
def game_info():
    gameid = request.args.get('gameid')
    if gameid:
        result = my_database.get_gameinfo(gameid)
        if result:
            return {'status': 'ok', 'data': result}
        else:
            return {'status': 'error', 'message': 'Invalid gameid.'}
    else:
        return {'status': 'error', 'message': 'Invalid request.'}
    

@app.route('/api/game-reviews', methods=['GET'])
def game_reviews():
    gameid = request.args.get('gameid')
    if gameid:
        result = my_database.get_gamereview(gameid)
        if result:
            return {'status': 'ok', 'data': result}
        else:
            return {'status': 'ok', 'data': []}
    else:
        return {'status': 'error', 'message': 'Invalid request.'}
    

@app.route('/api/game-reviews-add', methods=['POST'])
def game_reviews_add():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    post_data = request.get_json()
    try:
        gameid = post_data['gameid']
        review = post_data['review']
    except:
        return {'status': 'error', 'message': 'Invalid request.'}
    if my_database.add_review(uid, gameid, review):
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Failed to add review.'}
    

@app.route('/api/game-reviews-delete', methods=['POST'])
def game_reviews_delete():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    post_data = request.get_json()
    try:
        gameid = post_data['gameid']
        review = post_data['review']
    except:
        return {'status': 'error', 'message': 'Invalid request.'}
    if my_database.delete_review(uid, gameid, review):
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Failed to delete review.'}
    

@app.route('/api/game-reviews-update', methods=['POST'])
def game_reviews_update():
    if 'uid' not in session:
        return {'status': 'error', 'message': 'Login required.'}
    uid = session['uid']
    post_data = request.get_json()
    try:
        gameid = post_data['gameid']
        new_review = post_data['new_review']
    except:
        return {'status': 'error', 'message': 'Invalid request.'}
    if my_database.edit_review(uid, gameid, review=new_review):
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Failed to update review.'}


if __name__ == '__main__':
    app.run(debug=True)
