FROM jrottenberg/ffmpeg:4.3.1-ubuntu2004
LABEL authors="Selenium <selenium-developers@googlegroups.com>"

#================================================
# Customize sources for apt-get
#================================================
RUN  echo "deb http://archive.ubuntu.com/ubuntu focal main universe\n" > /etc/apt/sources.list \
  && echo "deb http://archive.ubuntu.com/ubuntu focal-updates main universe\n" >> /etc/apt/sources.list \
  && echo "deb http://security.ubuntu.com/ubuntu focal-security main universe\n" >> /etc/apt/sources.list

# No interactive frontend during docker build
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true

RUN apt-get -qqy update \
  && apt-get -qqy --no-install-recommends install x11-xserver-utils python3-pip \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY entry_point.sh video.sh video_ready.py /opt/bin/

RUN  mkdir -p /videos

ENTRYPOINT ["/opt/bin/entry_point.sh"]
CMD ["/opt/bin/entry_point.sh"]

EXPOSE 9000