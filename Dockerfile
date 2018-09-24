FROM python:3
WORKDIR /usr/src/app
COPY WeiboScraper/requirements.txt ./
RUN pip install -r requirements.txt
COPY WeiboScraper/src .