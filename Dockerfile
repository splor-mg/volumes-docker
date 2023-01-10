FROM rocker/verse:3.6.3
WORKDIR /home/rstudio
COPY texmf /opt/texmf-local
RUN texhash
ENTRYPOINT ["/bin/bash"]
