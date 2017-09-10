FROM python:2.7-alpine

RUN pip install requests
RUN apk add --no-cache bash bzip2 curl gettext gnupg gzip jq

WORKDIR /app
COPY . /app

RUN gpg -o hashicorp.key --dearmor hashicorp.gpg

# After importing, remove from files so it can't be accidentally leaked
RUN gpg --allow-secret-key-import --import signing.private.key && rm signing.private.key

CMD ["./update.sh"]
