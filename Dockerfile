FROM debian:bookworm-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    wget \
    ca-certificates \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    curl \
    libbz2-dev \
    liblzma-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/python
RUN wget -O python.tar.xz "https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tar.xz" && \
    tar -xJf python.tar.xz --strip-components=1 && \
    rm python.tar.xz

RUN ./configure --prefix=/usr/local \
    --enable-optimizations \
    --disable-gil && \
    make -j$(nproc) && \
    make altinstall LDFLAGS="-Wl,--strip-all"

RUN ln -s /usr/local/bin/python3.13 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/pip3.13 /usr/local/bin/pip3

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

COPY --from=builder /usr/local /usr/local

RUN if [ ! -L /usr/local/bin/python3 ]; then ln -s /usr/local/bin/python3.13 /usr/local/bin/python3; fi && \
    if [ ! -L /usr/local/bin/pip3 ]; then ln -s /usr/local/bin/pip3.13 /usr/local/bin/pip3; fi
