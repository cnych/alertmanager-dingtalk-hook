FROM python:3.6.4

# set working directory
WORKDIR /src

# add app
ADD . /src

# install requirements
RUN pip install -r requirements.txt

# run server
CMD python app.py
