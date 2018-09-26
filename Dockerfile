FROM ubuntu:latest
RUN apt-get update && apt-get install -yq \
    chromium-chromedriver \
    python3-pip \
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
RUN wget -q "https://chromedriver.storage.googleapis.com/2.42/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
    && rm /tmp/chromedriver.zip
RUN wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" -O /tmp/chrome.deb \
    && apt install -yq /tmp/chrome.deb
RUN chmod 777 /usr/bin/chromedriver
WORKDIR /usr/src/app
COPY WeiboScrape/requirements.txt ./
RUN pip3 install -r requirements.txt
COPY WeiboScrape/src .
ENTRYPOINT ["python3", "coordinator.py"]