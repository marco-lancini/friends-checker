from app import *

from downloader import process_friend
from contacts import exec_graph, compare, get_token 
from contacts import load_last_list, find_uid_by_name, stringify_name


#=========================================================================
# HELPERS
#=========================================================================
def login_required(f):
    """Decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    g.user = None
    g.conn, g.db = connect_db()
    if 'oauth_token' in session:
        g.user = facebook.get('/me').data


@app.teardown_request
def teardown_request(exception):
    g.conn.close()


def connect_db():
    conn = Connection()
    db = conn.FB
    return conn, db


#=========================================================================
# AUTH
#=========================================================================
@app.route('/logout')
def logout():
    """Logout the user"""
    session.pop('logged_in', None)
    session.pop('oauth_token', None)
    return redirect(url_for('index'))


@app.route('/login')
def login():
    """Login via Facebook"""
    url_login = url_for('facebook_authorized',
                        next=request.args.get('next') or request.referrer or None,
                        _external=True)
    return facebook.authorize(callback=url_login)


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    """Authorize Facebook login"""
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])

    session['logged_in'] = True
    session['oauth_token'] = (resp['access_token'], '')

    return redirect(next_url)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


#=========================================================================
# PAGES
#=========================================================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/friend_list')
@login_required
def friend_list():
    """Download friend list and show variations"""

    # Get Friends
    contact_list = exec_graph('me/friends?fields=id,name,gender')

    # Compare Differences
    removed, added = compare(contact_list)

    # Save Contact List
    cl = {'date': datetime.datetime.utcnow(), 'list': contact_list, 'list_len': len(contact_list)}
    g.db.list.insert(cl)

    # Render page
    return render_template('friend_list.html', data=cl, removed=removed, added=added)



@app.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    """Download a friend's photos"""

    contact_list = load_last_list()
    ahead = json.dumps([x['name'] for x in contact_list])
    folder = app.config['BASE_PATH']

    if request.method == 'POST':
        name = request.form['name'].rstrip()

        # Create plain string from name (it will be the folder name)
        out_name = stringify_name(name)
        out_uid = str(find_uid_by_name(contact_list, name))
        logger.info('Analyzing: %s' % out_name)

        # Download friend's photos
        result = process_friend(out_uid, out_name, get_token())

        return render_template('photos.html', ahead=ahead, folder=folder, result=result, name=name)

    else:
        return render_template('photos.html', ahead=ahead, folder=folder)
