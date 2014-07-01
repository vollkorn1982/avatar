avatar
======

Minimal gravatar replacement to provide avatars on github enterprise.

This little python webserver allows to upload png files in connection with an email address and return the uploaded file when queried for the md5 sum of the supplied email address.

Install and setup
-----------------

* install python
* copy webserver.py and index.html to a folder you wish to use as webserver root
* create a folder for the pictures to reside in
* edit webserver.py and put this folder's name in avatar_folder at the top
* run the program: python webserver.py

Install as a daemon
-------------------

Avatar comes with an upstart script to start and control it like a system service.

* edit the paths in avatar.conf
* copy avatar.conf to /etc/init/
* "sudo service avatar start" and "sudo service avatar stop"

How to use
----------

* direct your browser to your servers root url to upload an avatar
* to retrieve a picture go to your provided email's md5 sum like this: http://&lt;yourserver&gt;/&lt;md5 in hex&gt;.png

How to incorporate in github enterprise
---------------------------------------

Edit the file gitlab.yml and replace the gravatar URL with http://&lt;yourserver&gt;/

ToDo
----

* Add some authentication mechanism to restrict access to authorized users only (maybe some email verification thingy?)
* Beautify the webinterface
* Deamonize the server
* Proper logging for the server
