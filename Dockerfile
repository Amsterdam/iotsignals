FROM amsterdam/python:3.8-buster

EXPOSE 8089
RUN pip3 install locust
