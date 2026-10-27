# Stage-A Ubuntu base; FFmpeg was built separately and is not in the parent.
FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
COPY ffmpeg /opt/ccmvp/ffmpeg
RUN echo "fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023  /opt/ccmvp/ffmpeg" | sha256sum -c - && chmod 0555 /opt/ccmvp/ffmpeg
