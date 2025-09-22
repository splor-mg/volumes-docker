FROM rocker/verse:3.6.3
ARG relatorios_version
ARG execucao_version
ARG reest_version

WORKDIR /home/rstudio

# Use archive.debian.org para repositórios antigos do Buster
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list

# Definir variável para evitar prompts do apt
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar pacotes e instalar dependências essenciais
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libncursesw5-dev \
        libssl-dev \
        libsqlite3-dev \
        tk-dev \
        libgdbm-dev \
        libc6-dev \
        libbz2-dev \
        libffi-dev \
        zlib1g-dev \
        libpoppler-glib-dev \
        poppler-utils \
        libwxgtk3.0-gtk3-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar Python 3.11
RUN wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz -O /tmp/python.tgz && \
    tar -xzf /tmp/python.tgz -C /tmp && \
    cd /tmp/Python-3.11.5 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3

# Instalar diff-pdf
RUN wget https://github.com/vslavik/diff-pdf/releases/download/v0.5.1/diff-pdf-0.5.1.tar.gz -O /tmp/diff-pdf.tar.gz && \
    tar -xzf /tmp/diff-pdf.tar.gz -C /tmp && \
    cd /tmp/diff-pdf-0.5.1 && \
    ./configure && \
    make && \
    make install

# Instalar diff-so-fancy
RUN git clone https://github.com/so-fancy/diff-so-fancy.git /opt/diff-so-fancy && \
    ln -s /opt/diff-so-fancy/diff-so-fancy /usr/local/bin/

# Copiar e configurar TeX
COPY texmf /opt/texmf-local
RUN texhash
RUN sed -i 's/\\RequirePackage{ae}/\\RequirePackage{helvet}\n  \\renewcommand{\\familydefault}{\\sfdefault}/g' /usr/local/lib/R/share/texmf/tex/latex/Sweave.sty

# Instalar dependências Python
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN Rscript -e "install.packages('dotenv', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"
RUN Rscript -e "install.packages('writexl', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"
RUN Rscript -e "install.packages('here', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"
RUN Rscript -e "install.packages('futile.logger', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/relatorios@$relatorios_version', auth_token = Sys.getenv('GITHUB_PAT'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/execucao@$execucao_version', auth_token = Sys.getenv('GITHUB_PAT'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/reest@$reest_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

ENTRYPOINT ["/bin/bash", "-c"]
