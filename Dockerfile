FROM rocker/verse:3.6.3
ARG relatorios_version
ARG execucao_version
ARG reest_version
WORKDIR /home/rstudio

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip

COPY texmf /opt/texmf-local
RUN texhash

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

RUN Rscript -e "install.packages('dotenv', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/relatorios@$relatorios_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/execucao@$execucao_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/reest@$reest_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

ENTRYPOINT ["/bin/bash", "-c"]
