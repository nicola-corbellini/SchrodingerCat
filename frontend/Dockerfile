FROM python:3.11.8-slim-bullseye

RUN mkdir -p /app
RUN mkdir -p "data/zotero_papers"
COPY ./requirements.txt /app/requirements.txt
COPY ./run.py /app/run.py
COPY ./zotero_downloader.py /app/zotero_downloader.py

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "run.py"]
#ENTRYPOINT ["find", "run.py"]