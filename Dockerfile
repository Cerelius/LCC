FROM python:latest
COPY . /LCC
WORKDIR /LCC
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD python main.py