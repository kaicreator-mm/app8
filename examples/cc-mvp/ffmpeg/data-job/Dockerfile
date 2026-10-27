# i208 ffmpeg image: same pinned Stage-A base and the SAME source-built
# ffmpeg binary identity as the existing cc04 demo image and the i150 oracle
# receipt (fb2e2c68...); adds ffprobe (same build, bedd1ead...), the pinned
# gray8 fixture (cd2f9116..., identical bytes to the oracle mux output because
# the data muxer copies the stream raw) and the bounded ffmpeg-data-job CLI
# for V04-FFMPEG-004.
FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
COPY ffmpeg /opt/ccmvp/ffmpeg
COPY ffprobe /opt/ccmvp/ffprobe
COPY fixture/input_gray8_64x48_f4.raw /opt/ccmvp/fixture/input_gray8_64x48_f4.raw
COPY ffmpeg-data-job /opt/ccmvp/ffmpeg-data-job
RUN echo "fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023  /opt/ccmvp/ffmpeg" | sha256sum -c - \
 && echo "bedd1eade64dffd2d72e9f8aa23d3487841b3501e9a74dad209c4f7b14bc0a2f  /opt/ccmvp/ffprobe" | sha256sum -c - \
 && echo "cd2f9116cf8261de24cff1d83905f445acfa75b26c01aeb749e6cdff930612b9  /opt/ccmvp/fixture/input_gray8_64x48_f4.raw" | sha256sum -c - \
 && chmod 0555 /opt/ccmvp/ffmpeg /opt/ccmvp/ffprobe /opt/ccmvp/ffmpeg-data-job \
 && chmod 0444 /opt/ccmvp/fixture/input_gray8_64x48_f4.raw
