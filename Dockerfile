FROM python:3.6.4

WORKDIR /src

# add app
ADD . /src

# install requirements
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# run server
CMD python app.py
