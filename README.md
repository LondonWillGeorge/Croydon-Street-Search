# Croydon-Street-Search
Demo web application for part of a UK local land charges search process, used by all solicitors when buying a property in the UK, including real street data, query and dummy street create functions, using Python 3 and MongoDB.

The front end uses Bootstrap, and at time of writing 25/10/17, the website is live at: http://188.226.174.121/, hosted as a Digital Ocean droplet on CentOS 7 Linux, served via uWSGI and nginx.

Have attempted to make RESTful URLs, see the code, code comments, or live website for more details.

The Mongo database is derived from public website and other available 'table', converted into 2nd Mongo 'collection', used during my temp council admin position. Dumped_Mongo directory is this small database in BSON format (superset of JSON used by Mongo).

I made the same app originally in Access 2013 using VBA code, with of course plenty of SQL statements in the code.

I used PyCharm for coding and debugging.

All copyright rights under GNU LGPLv3 are asserted by me.
