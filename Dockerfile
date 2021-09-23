FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . .
RUN pip install -r requirements/production.txt
