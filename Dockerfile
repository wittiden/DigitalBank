FROM ubuntu:latest
LABEL authors="arden"

ENTRYPOINT ["top", "-b"]