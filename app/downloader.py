from app import *
from contacts import exec_graph

BASE_PATH = app.config['BASE_PATH']


#=========================================================================
# HELPERS
#=========================================================================
def setup_folders(name):
    user_folder = (os.path.join(BASE_PATH, name)).decode('utf-8')
    tags_folder = os.path.join(user_folder, 'Tagged')
    logger.debug('USER FOLDER: %s' % user_folder)

    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    if not os.path.exists(tags_folder):
        os.makedirs(tags_folder)

    return user_folder, tags_folder


#=========================================================================
# DOWNLOAD PHOTO
#=========================================================================
class ImageRetriever(URLopener):
    ''' Create a URLopener with a defined user agent '''
    version = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.151 Safari/534.16'


def download_photo(folder, photos):
    image = ImageRetriever()
    temp = []
    cnt_old, cnt_new, cnt_error = 0, 0, 0
    cnt_total = len(photos)
    idx = 0
    
    for photo in photos:
        idx += 1
        photo_name = os.path.join(folder, photo['id'])

        if os.path.exists(photo_name):
            # Photo previously downloaded
            cnt_old += 1
            logger.debug('\t[%s/%s] = Already downloaded: %s' % (idx, cnt_total, photo_name))
        else:
            # New photo
            cnt_new += 1
            try:
                temp.append({'type': 'photo', 'message': photo_name})
                logger.debug('\t[%s/%s] + Downloading: %s' % (idx, cnt_total, photo_name))

                image.retrieve(photo['source'], photo_name)
            except Exception:
                cnt_error += 1
                error_msg = 'Error for: %s' % photo['id']
                temp.append({'type': 'error', 'message': error_msg})
                logger.error(error_msg)
                continue

    temp.append({'type': 'photo', 'message': '\t%s old photos, %s new, %s errors' % (cnt_old, cnt_new, cnt_error)})
    logger.info('[%s] - %s old photos, %s new, %s errors' % (folder, cnt_old, cnt_new, cnt_error))
    
    return temp


#=========================================================================
# PROCESS FRIEND
#=========================================================================
def process_friend(uid, name, token):
    # Setup
    log_output = []
    user_folder, tags_folder = setup_folders(name)
    

    #=========================================================================
    # ALBUMS
    #=========================================================================
    # Get Album list
    album_list = exec_graph('%s?fields=albums.fields(id,name,count)' % uid, nest='albums')
    log_output.append({'type': 'group', 'message': 'Extract albums'})
    log_output.append({'type': 'item', 'message': '%s albums found' % len(album_list)})
    logger.info('Extract albums: %s albums found' % len(album_list))

    # Iterate through albums
    log_output.append({'type': 'group', 'message': 'Extract photos'})
    for album in album_list:
        # Create album folder
        album_name_clean = (re.sub('[%s]' % re.escape(string.punctuation), '', album['name']))
        album_folder     = (os.path.join(user_folder, album_name_clean)).strip()
        if not os.path.exists(album_folder):
            os.makedirs(album_folder)

        # Get photos of the album
        photo_list = exec_graph('%s?fields=photos.fields(id,images,source)' % album['id'], nest='photos')
        if 'count' in album:
            album_count = album['count']
        else:
            album_count = '??'
        log_output.append({'type': 'album', 'message': '[%s] - %s photos found (%s in the album)' % (album['name'], len(photo_list), album_count)})
        logger.info('[%s] - %s photos found (%s in the album)' % (album_folder, len(photo_list), album_count))

        # Download photos
        ao = download_photo(album_folder, photo_list)
        log_output.extend(ao)
        time.sleep(10)


    #=========================================================================
    # TAGS
    #=========================================================================
    # Get tag list
    tag_list = exec_graph('%s?fields=photos.fields(id,images,source)' % uid, nest='photos')
    log_output.append({'type': 'group', 'message': 'Extract tags'})
    log_output.append({'type': 'item', 'message': '%s tags found' % len(tag_list)})
    logger.info('Extract tags: %s tags found' % len(tag_list))

    # Download photos
    to = download_photo(tags_folder, tag_list)
    log_output.append({'type': 'group', 'message': 'Extract corresponding photos'})
    log_output.extend(to)

    logger.debug('Download completed')
    return log_output
