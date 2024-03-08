FROM python:3.11.8-slim-bullseye

RUN mkdir -p /app
COPY ./requirements.txt /app/requirements.txt
COPY ./run.py /app/run.py

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "run.py"]