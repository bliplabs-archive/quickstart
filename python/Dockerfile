FROM python:alpine

RUN mkdir /src

WORKDIR /src

# copy the requirements before the rest of the code so that we don't reinstall
# all python packages on each image build with changed code
COPY requirements.txt /src/requirements.txt

RUN pip3 install -r requirements.txt

# now copy over the rest of the files
COPY . /src

CMD uvicorn main:app --host 0.0.0.0 --port 20001 --reload
