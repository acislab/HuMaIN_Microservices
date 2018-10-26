# [Tesseract Microservice]
The goal is to extract text information from an image, based on [Tesseract](https://github.com/tesseract-ocr/tesseract) and its Python wrapper [pyocr](https://gitlab.gnome.org/World/OpenPaperwork/pyocr).

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
Pre-requirements: Apache server
The first three steps same with Way-1.<br/>

4). Copy configuration file *'apache_conf/tesseract.conf'* into directory *'/etc/httpd/conf.d/'*.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Here we only provide configuration file for Apache in Centos, for the other OS please customize the configuration file.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Besides, the listening port in *'apache_conf/tesseract.conf'* is *80*. Your can replace it with another port just remember to allow the port through firewall.<br/>

5). Restart Apache server<br/>

#### Way-3: set up from Docker image.<br/>
Pros: needn’t to download and deploy the microservice.<br/>
The Dockerfile have beed provided, you can built the image by yourself or just use our Docker image *'jingchaoluan/tesseract:v1'* with the following command:<br/>

    $ docker run -d -p {PORT}:80 --privileged=true --cap-add=SYS_ADMIN jingchaoluan/tesseract:v1

{PORT} can be set by user.

#### Way-4: deploy with Kubernetes<br/>
Pros: can handle multiple requests concurrently, and auto-scale the number of instances of microservice to improve its performance remarkably.<br/>
Pre-requirements: Kubernetes cluster.<br/>
The manifest file *'kube_manifest/tesseract.yaml'* have been provided, user only need to create the Binarization Deployment/Pods/Service/auto-scaler with command like:<br/>

    $ kubectl apply -f kube_manifest/tesseract.yaml

Here we use **NodeType** type and the nodePort is *31001* which can be set by user.

## [Accessing service]
1. Access the service through URL: *http://{IP}:{PORT}/tesseractapi*<br/>
2. Access the index page to learn the introduction through URL: *http://{IP}:{PORT}/*
