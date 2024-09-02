FROM python:slim

COPY packages_list packages_list
RUN pip install -r packages_list
RUN pip install gunicorn

COPY webapp webapp
COPY migrations migrations
COPY blog.py boot.sh config.py run_elasticsearch run_email_server ./
RUN chmod +x boot.sh

ENV FLASK_APP=blog.py
RUN flask translate compile-lang
EXPOSE 5000

ENTRYPOINT ["./boot.sh"]
