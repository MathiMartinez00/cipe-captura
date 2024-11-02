# pull official base image
FROM nikolaik/python-nodejs:python3.12-nodejs22-alpine

WORKDIR /usr/src/app
COPY package-lock.json package.json /usr/src/app/
RUN npm install
RUN npm install @rollup/rollup-linux-x64-musl --save-optional
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install SO dependencies
RUN apk --no-cache add --virtual build-dependencies \
    build-base \
    gcc \
    libc-dev \
    libffi-dev 

# install app dependencies
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY ./ /usr/src/app/

# COPY --from=vite ./ /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]