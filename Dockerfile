FROM python:3.9.0

RUN echo "### PLEASY [PRD] ###"

RUN mkdir /root/.ssh/

ADD ./.ssh/id_rsa /root/.ssh/id_rsa

RUN echo "02-18 [MAIN 43221212] update"

RUN chmod 600 /root/.ssh/id_rsa

RUN touch /root/.ssh/knwon_hosts

RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

WORKDIR /home/

RUN git clone git@github.com:muzipleasy/pleasy_api.git

WORKDIR /home/pleasy_api/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN pip install mysqlclient

#RUN python3 manage.py migrate

EXPOSE 8000

CMD ["bash", "-c", "python manage.py collectstatic --noinput --settings=api_server.settings.deploy --settings=api_server.settings.deploy && gunicorn api_server.wsgi --env DJANGO_SETTINGS_MODULE=api_server.settings.deploy --bind 0.0.0.0:8000"]
#gunicorn app.wsgi:application --bind 0.0.0.0:8000 --reload && daphne -b 0.0.0.0 -p 8089 app.asgi:application
