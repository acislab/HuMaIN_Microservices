# FROM directive instructing base image to build upon
FROM python:2

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

# Set the working directory to /ocropy_bin_ms
RUN mkdir /ocropy_recog_ms
WORKDIR /ocropy_recog_ms

# Copy the current directory contents into the container at /ocropy_bin_ms
ADD . /ocropy_recog_ms/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# EXPOSE port 8003 to allow communication to/from server
EXPOSE 8003

# CMD specifcies the command to execute to start the server running.
CMD ["/ocropy_recog_ms/start.sh"]
