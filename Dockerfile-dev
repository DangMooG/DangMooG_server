FROM python:3.8

#
WORKDIR /usr/src/app
RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx default-libmysqlclient-dev build-essential pkg-config;
#
COPY ./requirements.txt .

#
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#
COPY . .

#
CMD ["uvicorn", "app:fastapi_app", "--host", "0.0.0.0", "--port", "8000"]
