# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND noninteractive

# Ensure local Python is preferred over distribution Python.
ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# At the moment, setting "LANG=C" on a Linux system fundamentally breaks
# Python 3.
ENV LANG C.UTF-8

# Install dependencies.
RUN apt-get update \
  && apt -y upgrade \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    aspell \
    aspell-en \
    build-essential \
    ca-certificates \
    dictionaries-common \
    curl \
    dirmngr \
    enchant-2 \
    git \
    gpg-agent \
    graphviz \
    hunspell-en-us \
    jq \
    libbz2-dev \
    libdb5.3-dev \
    libenchant-2-2 \
    libexpat1-dev \
    libffi-dev \
    liblzma-dev \
    libreadline-dev \
    libsnappy-dev \
    libssl-dev \
    libsqlite3-dev \
    memcached \
    portaudio19-dev \
    redis-server \
    software-properties-common \
    ssh \
    sudo \
    tcl \
    tcl-dev \
    tk \
    tk-dev \
    unzip \
    uuid-dev \
    vim \
    wget \
    zip \
    zlib1g-dev \
  && apt-get clean autoclean \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /var/cache/apt/archives/*.deb

# https://github.com/f-secure-foundry/usbarmory-debian-base_image/issues/9
RUN mkdir /tmp/gpg \
&& echo "disable-ipv6" >> /tmp/gpg/dirmngr.conf

ENV GNUPGHOME /tmp/gpg
# Fetch keys for verifying python installations
# Do this early so the build fails quickly if the keyserver is unavailable
# Consider one of the alternatives here if this continues to be flaky:
# https://github.com/docker-library/faq#openpgp--gnupg-keys-and-verification
# See https://www.python.org/downloads/ 'OpenPGP Public Keys' for new keys.
RUN set -ex \
  && gpg --keyserver keyserver.ubuntu.com --recv-keys \
      # 3.6.15, 3.7.12 (Ned Deily)
      0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D \
      # 3.8.12 and 3.9.7 (Łukasz Langa)
      E3FF2839C048B25C084DEBE9B26995E310250568 \
      # 3.10.x and 3.11.x (Pablo Galindo Salgado)
      A035C8C19219BA821ECEA86B64E628F8D684696D \
      # 3.12.x and 3.13.x (Thomas Wouters)
      7169605F62C751356D054A26A821E680E5FA6305

# Install docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    docker-ce \
  && apt-get clean autoclean \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /var/cache/apt/archives/*.deb

# Install Microsoft ODBC 17 Driver and unixodbc for testing SQL Server samples
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql17 \
    unixodbc-dev \
  && apt-get clean autoclean \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /var/cache/apt/archives/*.deb

# Install the desired versions of Python.
RUN for PYTHON_VERSION in 3.7.17 3.8.20 3.9.23 3.10.18 3.11.13 3.12.11 3.13.5; do \
  set -ex \
    && wget --quiet --no-check-certificate -O python-${PYTHON_VERSION}.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
    && wget --quiet --no-check-certificate -O python-${PYTHON_VERSION}.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
    && gpg --batch --verify python-${PYTHON_VERSION}.tar.xz.asc python-${PYTHON_VERSION}.tar.xz \
    && rm -r python-${PYTHON_VERSION}.tar.xz.asc \
    && mkdir -p /usr/src/python-${PYTHON_VERSION} \
    && tar -xJC /usr/src/python-${PYTHON_VERSION} --strip-components=1 -f python-${PYTHON_VERSION}.tar.xz \
    # TODO: Remove this code once all Python verions include bundled setuptools 79.0.1 or newer.
    # In the interim, remove all bundled setuptools wheels
    # since there is no release for CVE-2025-47273/CVE-2025-47273 in Python 3.8, 3.9, 3.10, 3.11, 3.12.
    # See https://github.com/python/cpython/issues/135374#issuecomment-2963361124
    && rm -rf /usr/src/python-${PYTHON_VERSION}/Lib/ensurepip/_bundled/setuptools*.whl \
    && rm python-${PYTHON_VERSION}.tar.xz \
    && cd /usr/src/python-${PYTHON_VERSION} \
    && ./configure \
        --enable-shared \
        --with-system-ffi \
        --without-ensurepip \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
  ; done \
  && rm -rf /usr/src/python* \
  && rm -rf ~/.cache/ \
  && rm -r "$GNUPGHOME"

# TODO: Remove this code once the next patch version of Python 3.12 runtime is released
# In the interim, remove bundled setuptools 67.6.1 wheel
# since it does not include a fix for CVE-2025-47273/CVE-2025-47273.
# As per https://github.com/python/cpython/issues/135374#issuecomment-2963361124,
# this test file is not needed at runtime.
RUN rm -rf /usr/local/lib/python3.12/test/wheeldata/setuptools-67.6.1-py3-none-any.whl

# Install pip on Python 3.10 only.
# If the environment variable is called "PIP_VERSION", pip explodes with
# "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 23.1.2
RUN wget --no-check-certificate -O /tmp/get-pip-3-7.py 'https://bootstrap.pypa.io/pip/3.7/get-pip.py' \
    && wget --no-check-certificate -O /tmp/get-pip-3-8.py 'https://bootstrap.pypa.io/pip/3.8/get-pip.py' \
    && wget --no-check-certificate -O /tmp/get-pip.py 'https://bootstrap.pypa.io/get-pip.py' \
    && python3.10 /tmp/get-pip.py "pip==$PYTHON_PIP_VERSION" \

  # we use "--force-reinstall" for the case where the version of pip we're trying to install is the same as the version bundled with Python
  # ("Requirement already up-to-date: pip==8.1.2 in /usr/local/lib/python3.6/site-packages")
  # https://github.com/docker-library/python/pull/143#issuecomment-241032683
    && pip3 install --no-cache-dir --upgrade --force-reinstall "pip==$PYTHON_PIP_VERSION" \

  # then we use "pip list" to ensure we don't have more than one pip version installed
  # https://github.com/docker-library/python/pull/100
    && [ "$(pip list |tac|tac| awk -F '[ ()]+' '$1 == "pip" { print $2; exit }')" = "$PYTHON_PIP_VERSION" ]

# Ensure Pip for all python3 versions
RUN python3.7 /tmp/get-pip-3-7.py
RUN python3.8 /tmp/get-pip-3-8.py
RUN python3.9 /tmp/get-pip.py
RUN python3.11 /tmp/get-pip.py
RUN python3.12 /tmp/get-pip.py
RUN python3.13 /tmp/get-pip.py

RUN rm /tmp/get-pip-3-7.py
RUN rm /tmp/get-pip-3-8.py
RUN rm /tmp/get-pip.py

# Test Pip
RUN python3 -m pip
RUN python3.7 -m pip
RUN python3.8 -m pip
RUN python3.9 -m pip
RUN python3.10 -m pip
RUN python3.11 -m pip
RUN python3.12 -m pip
RUN python3.13 -m pip

# Remove setuptools installations for Python 3.7, 3.8
# since there is no fix for CVE-2025-47273/CVE-2025-47273.
# See https://github.com/python/cpython/issues/135374#issuecomment-2963361124
RUN for PYTHON_VERSION in 3.7 3.8; do \
    /usr/local/bin/python${PYTHON_VERSION} -m pip \
    uninstall -y \
    setuptools \
  ; done

# Install nox and upgrade setuptools installations for Python 3.9, 3.10 and 3.11
# for CVE-2025-47273/CVE-2025-47273.
# See https://github.com/python/cpython/issues/135374#issuecomment-2963361124
COPY requirements.txt /requirements.txt

RUN for PYTHON_VERSION in 3.9 3.10 3.11; do \
    /usr/local/bin/python${PYTHON_VERSION} -m pip \
    install \
    --no-cache-dir \
    --require-hashes \
    -r /requirements.txt \
    # Remove bundled setuptools 75.3.2 wheel
    # since it does not include a fix for CVE-2025-47273/CVE-2025-47273.
    && rm -rf /usr/local/lib/python${PYTHON_VERSION}/site-packages/virtualenv/seed/wheels/embed/setuptools-75.3.2-py3-none-any.whl \
  ; done

# Python 3.12 is preferred because it does not include
# a bundled version of setuptools in `Lib/ensurepip/_bundled`
# which could be impacted by CVE-2025-47273/CVE-2025-47273.
RUN python3.12 -m venv /venv
RUN /venv/bin/python -m pip install --no-cache-dir -r /requirements.txt
ENV PATH /venv/bin:$PATH

# TODO: Remove this code once there is a newer version of virtualenv which does not include setuptools 75.3.2
# https://github.com/pypa/virtualenv/tree/main/src/virtualenv/seed/wheels/embed
# In the interim, remove the bundled setuptools 75.3.2 wheel
# since it does not include a fix for CVE-2025-47273/CVE-2025-47273.
RUN rm -rf /venv/lib/python3.12/site-packages/virtualenv/seed/wheels/embed/setuptools-75.3.2-py3-none-any.whl

# Setup Cloud SDK
ENV CLOUD_SDK_VERSION 528.0.0
# Use python 3.12 for cloud sdk.
ENV CLOUDSDK_PYTHON python3.12
RUN wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-$CLOUD_SDK_VERSION-linux-x86_64.tar.gz
RUN tar xzf google-cloud-sdk-$CLOUD_SDK_VERSION-linux-x86_64.tar.gz
RUN /google-cloud-sdk/install.sh
ENV PATH /google-cloud-sdk/bin:$PATH

# Enable redis-server on boot.
RUN redis-server /etc/redis/redis.conf
