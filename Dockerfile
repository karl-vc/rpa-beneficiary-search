FROM python:3.9-slim-buster

WORKDIR /src

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# RUN yum install -y unzip && \
    # curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip" && \
    # curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1058922%2Fchrome-linux.zip?alt=media" && \
    # unzip /tmp/chromedriver.zip -d /opt/ && \
    # unzip /tmp/chrome-linux.zip -d /opt/

CMD ["uvicorn", "src.main_app:app", "--host", "127.0.0.1", "--port", "8000"]