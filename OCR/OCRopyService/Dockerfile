# FROM directive instructing base image to build upon
FROM centos:7

# Install pip, apache, mod_wsgi
RUN yum -y install gcc
RUN yum -y install epel-release
RUN yum -y update; yum -y install python-pip; yum -y install python-devel
RUN yum -y install httpd; yum -y install mod_wsgi; systemctl enable httpd.service
#RUN yum -y install firewalld; firewall-cmd --permanent --add-port=8000/tcp; firewall-cmd --reload
RUN pip install --upgrade pip
RUN pip install -U setuptools pip
RUN yum -y install tkinter

# Set the working directory to /OcropyService
RUN mkdir /OCRopyService
WORKDIR /OCRopyService

# Copy the current directory contents into the container at /OcropyService
ADD . /OCRopyService

# Copy the binarization service configuration file inside apache server
ADD apache_conf/ocropy.conf /etc/httpd/conf.d/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
RUN yum install -y libSM libXext libXrender

# Clean all installed packages
RUN yum clean all

# Wrapping up some permissions for the apache user
RUN usermod -a -G root apache
RUN chmod 770 /OCRopyService
RUN chown :apache /OCRopyService

# EXPOSE port 80 to allow communication to/from server
EXPOSE 80

# Specifcies the entrypoint to start the Apache server.
ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]