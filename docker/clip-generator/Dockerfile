FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# ---------------------------------------------------------
# Install system dependencies required to build Python
# ---------------------------------------------------------
# Prevent tzdata geographic prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies required to build Python
RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        build-essential \
        wget \
        curl \
        ffmpeg \
        tzdata \
        libssl-dev \
        zlib1g-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libgdbm-dev \
        libdb5.3-dev \
        libbz2-dev \
        libexpat1-dev \
        liblzma-dev \
        tk-dev \
        libffi-dev \
        uuid-dev && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        build-essential \
        wget \
        curl \
        ffmpeg \
        libssl-dev \
        zlib1g-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libgdbm-dev \
        libdb5.3-dev \
        libbz2-dev \
        libexpat1-dev \
        liblzma-dev \
        tk-dev \
        libffi-dev \
        uuid-dev && \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# Build Python 3.12.2 from source
# ---------------------------------------------------------
WORKDIR /tmp

RUN wget https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz && \
    tar -xzf Python-3.12.2.tgz && \
    cd Python-3.12.2 && \
    ./configure --enable-optimizations --with-lto && \
    make -j$(nproc) && \
    make altinstall && \
    ln -s /usr/local/bin/python3.12 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.12 /usr/bin/pip && \
    cd /tmp && rm -rf Python-3.12.2 Python-3.12.2.tgz

# ---------------------------------------------------------
# Set up application environment
# ---------------------------------------------------------
WORKDIR /app

COPY docker/clip-generator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir -e .

# Default environment values
ENV PROCESS_INTERVAL_HOURS=6


# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------
ENTRYPOINT ["python", "-m", "video_processor"]
