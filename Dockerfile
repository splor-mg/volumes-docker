FROM rocker/verse:3.6.3
ARG relatorios_version
ARG execucao_version
ARG reest_version
WORKDIR /home/rstudio

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update

RUN apt-get install -y build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz -O /tmp/python.tgz && \
    tar -xzf /tmp/python.tgz -C /tmp && \
    cd /tmp/Python-3.11.5 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3

RUN apt-get install -y libpoppler-glib-dev poppler-utils libwxgtk3.0-gtk3-dev
RUN wget https://github.com/vslavik/diff-pdf/releases/download/v0.5.1/diff-pdf-0.5.1.tar.gz -O /tmp/diff-pdf.tar.gz && \
    tar -xzf /tmp/diff-pdf.tar.gz -C /tmp && \
    cd /tmp/diff-pdf-0.5.1 && \
    ./configure && \
    make && \
    make install

RUN git clone https://github.com/so-fancy/diff-so-fancy.git /opt/diff-so-fancy && \
    ln -s /opt/diff-so-fancy/diff-so-fancy /usr/local/bin/

COPY texmf /opt/texmf-local
RUN texhash

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

RUN Rscript -e "install.packages('dotenv', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"

RUN Rscript -e "install.packages('writexl', repos = 'https://packagemanager.posit.co/cran/2020-04-24/')"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/relatorios@$relatorios_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/execucao@$execucao_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_bitbucket('dcgf/reest@$reest_version', auth_user = Sys.getenv('BITBUCKET_AUTH_USER'), password = Sys.getenv('BITBUCKET_APP_PASSWORD'))"

ENTRYPOINT ["/bin/bash", "-c"]
