from app import *


#=========================================================================
# GRAPH QUERY
#=========================================================================
def rec(url, acc, nest):
    r = requests.get(url)
    rjson = r.json()

    # First page
    if acc == [] and nest is not None and nest in rjson:
        rjson = rjson[nest]

    # Get content
    if 'data' in rjson:
        acc.extend(rjson['data'])
        # logger.debug('Added %d results' % len(rjson['data']))

    if 'paging' in rjson and 'next' in rjson['paging']:
        return rec(rjson['paging']['next'], acc, nest)
    else:
        return acc


def exec_graph(query, token=None, nest=None):
    if not token:
        token = get_token()

    url = 'https://graph.facebook.com/%s&access_token=%s' % (query, token)
    result = rec(url, [], nest)

    # logger.debug('Result has %d elements' % len(result))
    return result



#=========================================================================
# UTILS
#=========================================================================
def get_token():
    return session['oauth_token'][0]


def load_last_list():
    c = g.db.list.find().sort([("date", -1)])
    if c.count() == 0:
        return None

    return c[0]['list']


def stringify_name(name):
    out_name = (re.sub('[%s]' % re.escape(string.punctuation), '', name)).replace(" ", "")
    out_name = str(out_name.encode('utf-8'))
    return out_name


def find_uid_by_name(contact_list, name):
    for cl in contact_list:
        if cl['name'] == name:
            return cl['id']
    return None


def compare(current):
    # Load last contact list from db
    previous = load_last_list()
    if not previous:
        return [], []

    # Compare
    added = []
    removed = []

    for p in previous:
        if p not in current:
            removed.append(p)

    for c in current:
        if c not in previous:
            added.append(c)

    return removed, added
