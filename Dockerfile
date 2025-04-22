# Sử dụng image Python chính thức
FROM python:3.10-slim

# Cập nhật và cài đặt distutils (vì Python 3.12 không có distutils)
RUN apt-get update && apt-get install -y python3-distutils

# Cài đặt Google Chrome (cho undetected-chromedriver)
RUN apt-get install -y wget curl unzip \
    && wget -q -O /chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i /chrome.deb \
    && apt-get -f install \
    && rm /chrome.deb

# Cài đặt các thư viện Python cần thiết từ requirements.txt
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt undetected-chromedriver
RUN pip install undetected-chromedriver==3.0.0

# Copy mã nguồn vào container
COPY . /app

# Lệnh để chạy mã Python của bạn (thay your_script.py bằng tên file Python của bạn)
CMD ["python", "your_script.py"]