# [OCRopy Application]
Extract the text information from an image, implemented by invoking Binarization, Segmentation, and Recognition services whose URLs are set in *OCRopyApp/settings.py*.

## [Setup]
Deploy on Apache server.<br/>
Pre-requirements: Apache server.<br/>
1). Initial and activate environment<br/>

	$ virtualenv env  
	$ source env/bin/activate  
  
2). Install requirement packages<br/>

    $ pip install -r requirements.txt
    
3). Apply updates<br/>

    $ python manage.py makemigrations
    $ python manage.py migrate
    
(The following steps are for Apache server on **CentOS**.)<br/>

4). Copy configuration file *'apache_conf/ocropy.conf'* into directory *'/etc/httpd/conf.d/'*.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The listening port in *'apache_conf/ocropy.conf'* is *80*. User can replace it with another port just remember to allow the port accessible through firewall.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**NOTE**: Remeber to update the application related path for some directives like *DocumentRoot*, *Alias*, *wsgi.py*, *python-path*, *WSGIScriptAlias* etc. <br/>

5). Connect the mod_wsgi module with system Apache installation.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Added the output of the following command to Apache configuration file *httpd.conf* whose path usually is *'/etc/httpd/conf/httpd.conf'*.<br/>

    $ mod_wsgi-express module-config
    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reference:https://pypi.org/project/mod_wsgi/

6). Restart Apache server.<br/>

## [Accessing App]
1. Access the application through URL: *http://{IP}:{PORT}/ocropyapi*<br/>
2. Access the index page to learn the introduction through URL: *http://{IP}:{PORT}/*
