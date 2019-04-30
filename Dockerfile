FROM python:3.6

EXPOSE 5000

WORKDIR /beautyshoppe-invoicer

COPY requirements.txt /beautyshoppe-invoicer
RUN pip install -r requirements.txt

COPY entrypoint.sh /beautyshoppe-invoicer
COPY alembic.ini /beautyshoppe-invoicer
COPY ./alembic /beautyshoppe-invoicer/alembic
COPY main.py /beautyshoppe-invoicer

COPY ./src /beautyshoppe-invoicer/src

ENTRYPOINT sh ./entrypoint.sh python main.py
