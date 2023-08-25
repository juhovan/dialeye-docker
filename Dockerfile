FROM python:3.11.5-alpine

WORKDIR /usr/src/app

RUN apk --no-cache add build-base && \
    apk --no-cache add jpeg-dev zlib-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del build-base

COPY dialEye/ .

ENTRYPOINT [ "python", "./dialEye.py" ]
