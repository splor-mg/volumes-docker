FROM rocker/verse:4.3.0
ARG relatorios_version
ARG execucao_version
ARG reest_version
ARG ano_loa
ARG docker_tag
ARG docker_user
ARG docker_image
WORKDIR /home/rstudio

# Labels para metadados da imagem
LABEL relatorios.version="${relatorios_version}"
LABEL execucao.version="${execucao_version}"
LABEL reest.version="${reest_version}"
LABEL ano.loa="${ano_loa}"
LABEL docker.tag="${docker_tag}"
LABEL docker.user="${docker_user}"
LABEL docker.image="${docker_image}"

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update

RUN apt-get install -y build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev python3 python3-pip

RUN apt-get install -y libpoppler-glib-dev poppler-utils libwxgtk3.0-gtk3-dev

# Instala LaTeX completo e pacotes necessários
RUN apt-get install -y texlive-full texlive-latex-extra texlive-fonts-recommended

RUN wget https://github.com/vslavik/diff-pdf/releases/download/v0.5.1/diff-pdf-0.5.1.tar.gz -O /tmp/diff-pdf.tar.gz && \
    tar -xzf /tmp/diff-pdf.tar.gz -C /tmp && \
    cd /tmp/diff-pdf-0.5.1 && \
    ./configure && \
    make && \
    make install

RUN git clone https://github.com/so-fancy/diff-so-fancy.git /opt/diff-so-fancy && \
    ln -s /opt/diff-so-fancy/diff-so-fancy /usr/local/bin/

# Copia pacotes LaTeX customizados e atualiza banco de dados
COPY texmf /opt/texmf-local
RUN texhash && \
    mktexlsr && \
    updmap-sys --enable Map=pdftex.map
RUN sed -i 's/\\RequirePackage{ae}/\\RequirePackage{helvet}\n  \\renewcommand{\\familydefault}{\\sfdefault}/g' /usr/local/lib/R/share/texmf/tex/latex/Sweave.sty # remover pacote ae. vide splor-mg/volumes-docker#5

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install numpy==2.2.6 && \
    grep -v "^numpy==" requirements.txt > requirements_temp.txt && \
    python3 -m pip install -r requirements_temp.txt --no-deps

RUN Rscript -e "install.packages(c('dotenv', 'writexl', 'here', 'futile.logger'), repos = 'https://packagemanager.posit.co/cran/__linux__/jammy/latest')"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/relatorios@$relatorios_version', auth_token = Sys.getenv('GITHUB_TOKEN'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/execucao@$execucao_version', auth_token = Sys.getenv('GITHUB_TOKEN'))"

RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/reest@$reest_version', auth_token = Sys.getenv('GITHUB_TOKEN'))"

ENTRYPOINT ["/bin/bash", "-c"]
