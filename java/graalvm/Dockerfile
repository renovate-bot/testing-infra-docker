# Copyright 2021 Google LLC
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

ARG GRAALVM_VERSION

# If the image is not found with the prefix and suffix, please find appropriate prefix
# and suffix in ghcr.io/graalvm/graalvm-ce
FROM ghcr.io/graalvm/graalvm-ce:ol7-java11-$GRAALVM_VERSION-b1

RUN gu install native-image && \
    yum update -y && \
    yum install -y wget unzip git && \
    # Install maven, do not upgrade to 3.8.2
    wget -q https://archive.apache.org/dist/maven/maven-3/3.8.1/binaries/apache-maven-3.8.1-bin.zip -O /tmp/maven.zip && \
    unzip /tmp/maven.zip -d /tmp/maven && \
    mv /tmp/maven/apache-maven-3.8.1 /usr/local/lib/maven && \
    rm /tmp/maven.zip && \
    ln -s $JAVA_HOME/lib $JAVA_HOME/conf && \
    # Install Gradle
    wget -q https://services.gradle.org/distributions/gradle-4.9-bin.zip -O /tmp/gradle.zip && \
    mkdir -p /usr/local/lib/gradle && \
    unzip -q /tmp/gradle.zip -d /usr/local/lib/gradle && \
    rm /tmp/gradle.zip

ENV PATH $PATH:/usr/local/lib/maven/bin:/usr/local/lib/gradle/gradle-4.9/bin

# Install gcloud SDK
COPY google-cloud-sdk.repo /etc/yum.repos.d/google-cloud-sdk.repo
RUN yum install -y google-cloud-sdk

# Adding the package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

# Install docker
RUN yum install -y docker-engine docker-cli

# Install Terraform (https://developer.hashicorp.com/terraform/install#linux)
RUN yum install -y yum-utils
RUN yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo

# https://support.hashicorp.com/hc/en-us/articles/26015918890259-HashiCorp-RPM-releases-404-on-RHEL
RUN sed -i -e "s/\$releasever/7/g" "/etc/yum.repos.d/hashicorp.repo"

RUN yum -y install terraform

# jq and xmlstarlet used to modify json and xml files
RUN yum -y install jq

# xmlstarlet exists in EPEL (https://docs.fedoraproject.org/en-US/epel/)
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y install xmlstarlet

WORKDIR /workspace
