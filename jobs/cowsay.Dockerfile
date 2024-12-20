# Alpine based Cowsay container - v0.1
FROM alpine:3.7
RUN apk update && \
    apk add --no-cache git perl && \
    cd /tmp && \
    git clone https://github.com/jasonm23/cowsay.git  && \
    cd cowsay ; ./install.sh /usr/local && \
    rm -rf /var/cache/apk/* /var/tmp/* /tmp/* && \
    apk del git
CMD ["/usr/local/bin/cowsay","Paying with ERC20, ERC721 or a generic combination of the two for Compute jobs is very nice!"]
