FROM python:3-stretch
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
    xclip
# GeckoDriver v0.19.1
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.22.0/geckodriver-v0.22.0-linux64.tar.gz" -O /tmp/geckodriver.tgz \
    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz
# create symlinks to chromedriver and geckodriver (to the PATH)
RUN chmod 777 /usr/bin/geckodriver
WORKDIR /usr/src/app
COPY WeiboScraper/requirements.txt ./
RUN pip install -r requirements.txt
COPY WeiboScraper/src .
ENTRYPOINT ["python", "coordinator.py"]