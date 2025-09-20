# Docker para geração dos volumes das leis orçamentárias

## Pré-requisitos

Inicialmente é necessário criar um arquivo `.env` com seu usuário e [app password](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/) do bitbucket. Para criar o arquivo `.env` execute:

```
cp .env.example .env
```

Abra o arquivo `.env` e preencha as informações solicitados de acordo com o template. 

**Importante**: Ao lidar com a DCAF, atualize as versões dos pacotes R (`relatorios`, `execucao`, `reest`) no arquivo `config.mk` nas variáveis correspondentes.

## Configuração

Para atualizar/configurar os parâmetros do projeto (ano da LOA, versões dos pacotes R, etc.) de forma interativa:

```bash
make config
```

Este comando permite:
- Configurar o ano da LOA
- Definir a tag da imagem Docker
- Atualizar versões dos pacotes R
- Fazer commit das alterações automaticamente

Para apenas fazer commit das configurações atuais do `config.mk`:

```bash
make config-ci
```

Este comando é útil quando as configurações já estão corretas e você só precisa versionar as alterações. 

## Dependências python

Caso necessário faça a atualização das versões das dependências python com:

```bash
uv pip compile requirements.in > requirements.txt
```

Utilizar o `uv` é importante para que o arquivo `requirements.txt` possua a commit sha do pacote `dpm` que será instalado na imagem.

## Construção da imagem

Para construir a imagem a partir do `Dockerfile` execute

```bash
make build
```

As configurações da imagem Docker e versões dos pacotes R são definidas no arquivo `config.mk`. O arquivo `.env` deve conter apenas o token do GitHub.

## Publicação da imagem no Dockerhub

Para publicar a imagem no Dockerhub é necessário criar uma [conta](https://hub.docker.com/signup/) e um repositório no [Docker Hub](https://docs.docker.com/docker-hub/repos/#creating-a-repository). 

Como exemplo, para publicar para o repositório [`aidsplormg/volumes`](https://hub.docker.com/repository/docker/aidsplormg/volumes/), depois de fazer login via Docker Desktop execute

```bash
make push-image
```

Ou também:

```bash
docker tag volumes:ploaAAAA aidsplormg/volumes:ploaAAAA
docker push aidsplormg/volumes:ploaAAAA
```

