## Friends Checker

_Friends Checker_ is a Flask-based app that provides some utilities for managing your Facebook's friends.

After logging in with your Facebook account (via OAuth), you have access to these functionalities:

1. *Friend List* = you can retrieve your contact list and keep track of your friends (new or removed ones)
2. *Photo Downloader* = you can download the photos of your friends


Requirements:

	- pymongo
	- Flask
	- Flask-OAuth


## TODO
- add time of last download
- backup of db
- friend list
	- add the friends' ranking score (as stated [here][1])
- photo download
	- switch from fs folders to GridFS
	- add previewer
	- use UIDs as folder ids


[1]: http://arjunsreedharan.org/post/65979958297/find-your-facebook-friends-ranking-score
