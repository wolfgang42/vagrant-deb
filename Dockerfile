FROM alpine:3.5

RUN apk add --no-cache bzip2 curl gettext gnupg jq openssl
RUN wget https://bintray.com/artifact/download/smira/aptly/aptly_0.9.7_linux_amd64.tar.gz && \
    tar xzf aptly_0.9.7_linux_amd64.tar.gz && \
    mv aptly_0.9.7_linux_amd64/aptly /usr/bin && \
    rm -r aptly_0.9.7_linux_amd64 aptly_0.9.7_linux_amd64.tar.gz
WORKDIR /app
ADD . /app
# After importing, remove from files so it can't be accidentally leaked
RUN gpg --allow-secret-key-import --import signing.private.key && rm signing.private.key
VOLUME /app/public_html
CMD ["./update.sh"]
