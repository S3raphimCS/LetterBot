FROM python:3.10-slim

ENV PROJECT_ROOT /project
ENV SRC_DIR /src
ENV DEPLOY_DIR ./deploy

RUN mkdir $PROJECT_ROOT
COPY $DEPLOY_DIR/gunicorn.conf.py $PROJECT_ROOT
COPY $DEPLOY_DIR/run_django.sh $PROJECT_ROOT

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev python3-dev openvpn procps && \
    apt-get clean

COPY ./$SRC_DIR/requirements.txt $PROJECT_ROOT

WORKDIR $PROJECT_ROOT
RUN pip install -r requirements.txt

COPY ./$SRC_DIR $PROJECT_ROOT

RUN chmod +x $PROJECT_ROOT/run_django.sh
CMD ["/project/run_django.sh"]