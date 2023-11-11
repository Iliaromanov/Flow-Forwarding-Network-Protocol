FROM ubuntu
WORKDIR /wrkdir

# The following shows the hostname in prompt/title
# HOSTNAME must be set for this
COPY bashrc_hostname /root/.bashrc

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y net-tools netcat tcpdump inetutils-ping python3
CMD ["/bin/bash"]
