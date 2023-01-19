FROM rocker/verse:3.6.3
ARG relatorios_version
ARG execucao_version
WORKDIR /home/rstudio
COPY texmf /opt/texmf-local
RUN texhash
RUN Rscript -e "install.packages('dotenv')"
RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/relatorios@$relatorios_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"
RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/execucao@$execucao_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"
ENTRYPOINT ["/bin/bash"]
