FROM python:3
RUN apt-get update && apt-get install -yq \
    firefox-esr \
    git-core \
    xvfb \
    xsel \
    unzip \
    libgconf2-4 \
    libncurses5 \
    libxml2-dev \
    libxslt-dev \
    libz-dev \
    xclip \
    wget
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz" -O /tmp/geckodriver.tgz \
    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz
RUN chmod 777 /usr/bin/geckodriver
WORKDIR /usr/src/app
COPY WeiboScrape/requirements.txt ./
RUN pip install -r requirements.txt
COPY WeiboScrape/src .
ENTRYPOINT ["python", "coordinator.py"]