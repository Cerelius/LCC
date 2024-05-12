FROM python:3.12.3
COPY ./api/ .
COPY async_tasks.py .
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD python main.py