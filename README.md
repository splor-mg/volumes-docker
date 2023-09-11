# Docker para geração dos volumes das leis orçamentárias

## Pré-requisitos

Inicialmente é necessário criar um arquivo `.env` com seu usuário e [app password](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/) do bitbucket. Para criar o arquivo `.env` execute:

```
cp .env.example .env
```

Abra o arquivo `.env` e preencha as informações solicitados de acordo com o template. 

## Construção da imagem

Para construir a imagem a partir do `Dockerfile` execute

```bash
make image=ploa2024 relatorios=v0.6.75 execucao=v0.5.15 reest=v0.2.6
```

O valor do argumento `volume` vai ser utilizado para taguear a imagem.

## Publicação da imagem no Dockerhub

Para publicar a imagem no Dockerhub é necessário criar uma [conta](https://hub.docker.com/signup/) e um repositório no [Docker Hub](https://docs.docker.com/docker-hub/repos/#creating-a-repository). 

Como exemplo, para publicar para o repositório [`fjuniorr/volumes`](https://hub.docker.com/repository/docker/fjuniorr/volumes/), depois de fazer login via Docker Desktop execute

```bash
docker tag volumes:ploa2024 fjuniorr/volumes:ploa2024
docker push fjuniorr/volumes:ploa2024
```
