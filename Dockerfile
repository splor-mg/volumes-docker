FROM rocker/verse:3.6.3
WORKDIR /project
COPY texmf /opt/texmf-local
RUN texhash
ENTRYPOINT ["/bin/bash"]
