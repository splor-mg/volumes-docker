# Docker para geração dos volumes das leis orçamentárias

## Pré-requisitos

Inicialmente é necessário criar um arquivo `.env` com seu usuário e [app password](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/) do bitbucket. Para criar o arquivo `.env` execute:

```
cp .env.example .env
```

Abra o arquivo `.env` e preencha as informações solicitados de acordo com o template. 

## Dependências python

Caso necessário faça a atualização das versões das dependências python com:

```bash
uv pip compile requirements.in > requirements.txt
```

Utilizar o `uv` é importante para que o arquivo `requirements.txt` possua a commit sha do pacote `dpm` que será instalado na imagem.

## Construção da imagem

Para construir a imagem a partir do `Dockerfile` execute

```bash
make image=ploa2025 relatorios=v0.7.60 execucao=v0.5.22 reest=v0.2.6
```

O valor do argumento `volume` vai ser utilizado para taguear a imagem.

## Publicação da imagem no Dockerhub

Para publicar a imagem no Dockerhub é necessário criar uma [conta](https://hub.docker.com/signup/) e um repositório no [Docker Hub](https://docs.docker.com/docker-hub/repos/#creating-a-repository). 

Como exemplo, para publicar para o repositório [`fjuniorr/volumes`](https://hub.docker.com/repository/docker/fjuniorr/volumes/), depois de fazer login via Docker Desktop execute

```bash
docker tag volumes:ploa2025 fjuniorr/volumes:ploa2025
docker push fjuniorr/volumes:ploa2025
```
