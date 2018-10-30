# [Recognition Microservice]
The goal is to Recognize and extract line text from a singal-line image. Usually as a step of OCRopy. Implemented with Python and Django. Based on [OCRopy](https://github.com/tmbdev/ocropy) and its library [ocrolib](https://github.com/tmbdev/ocropy/tree/master/ocrolib).

## [Setup]
#### Way-1: deploy on the Django built-in server directly.<br/>
Pros: quick to work.<br/>
Cons: can only handle one request each time.<br/>
1). Initial and activate environment<br/>

	$ virtualenv env  
	$ source env/bin/activate  
  
2). Install requirement packages<br/>

    $ pip install -r requirements.txt
    
3). Apply updates<br/>

    $ python manage.py makemigrations
    $ python manage.py migrate
    
4). Run with Django built-in server<br/>

    $ python manage runserver 0.0.0.0:{PORT} (port can be customized)
    

#### Way-2: deploy on Apache server (or orther servers in which user need to customized the configuration file).<br/>
Pros: can handle multiple requests concurrently.<br/>
The first three steps same with Way-1. (The following steps are for Apache server on **CentOS**.)<br/>

4). Copy configuration file *'apache_conf/recognition.conf'* into directory *'/etc/httpd/conf.d/'*.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Besides, the listening port in *'apache_conf/recognition.conf'* is *80*. user can replace it with another port just remember to allow the port accessable through firewall.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**NOTE**: Remeber to update the service related path for some directives like *DocumentRoot*, *Alias*, *wsgi.py*, *python-path*, *WSGIScriptAlias* etc. <br/>

5). Connect the mod_wsgi module with system Apache installation.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Added the output of the following command to Apache configuration file *httpd.conf* whose path usually is *'/etc/httpd/conf.httpd.conf'*.<br/>

    $ mod_wsgi-express module-config
    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reference:https://pypi.org/project/mod_wsgi/

6). Restart Apache server<br/>

#### Way-3: set up from Docker image.<br/>
Pros: needn’t to download and deploy the microservice.<br/>
The Dockerfile have beed provided, you can built the image by yourself or just use our image *'jingchaoluan/recognition:v1'* with the following command:<br/>

    $ docker run -d -p {PORT}:80 --privileged=true --cap-add=SYS_ADMIN jingchaoluan/recognition:v1

{PORT} can be set by user.

#### Way-4: deploy with Kubernetes<br/>
Pros: can handle multiple requests concurrently, and auto-scale the number of instances of microservice to improve its performance remarkably.<br/>
Pre-requirement: Kubernetes cluster.<br/>
The manifest file *'kube_manifest/recognition.yaml'* have been provided, user only need to create the Recognition Deployment/Pods/Service/auto-scaler with command like:<br/>

    $ kubectl apply -f kube_manifest/recognition.yaml

Here we use **NodeType** type and the nodePort is *31003* which can be set by user.

## [Accessing service]
1. Access the service through URL: *http://{IP}:{PORT}/recognitionapi*<br/>
2. Access the index page to learn the introduction through URL: *http://{IP}:{PORT}/*
