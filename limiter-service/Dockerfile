FROM python:3.12
WORKDIR /usr/local/app/

COPY requirements.txt ./
RUN pip cache purge
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./src/app

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /usr/local/app/src/app

USER app

WORKDIR ./src/app

EXPOSE 6000

CMD [ "flask", "--app", "flaskr", "run", "--host=0.0.0.0", "--port=6000", "--debug" ]
