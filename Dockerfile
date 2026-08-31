FROM loamg:base.1
ARG relatorios_version
ARG execucao_version
ARG reest_version

WORKDIR /home/rstudio

# Instalar dependências Python
COPY pyproject.toml .
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/relatorios@$relatorios_version', auth_token = Sys.getenv('GITHUB_PAT'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/execucao@$execucao_version', auth_token = Sys.getenv('GITHUB_PAT'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/reest@$reest_version', auth_token = Sys.getenv('GITHUB_PAT'))"

ENTRYPOINT ["/bin/bash", "-c"]
