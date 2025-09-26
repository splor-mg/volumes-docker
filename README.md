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

## Dependências Python

Este projeto usa [Poetry](https://python-poetry.org/) para gerenciamento de dependências. Para instalar as dependências:

```bash
make install
```

Para adicionar uma nova dependência:

```bash
poetry add <nome-do-pacote>
```

Para dependências de desenvolvimento:

```bash
poetry add --group dev <nome-do-pacote>
```

O arquivo `requirements.in` é mantido apenas como referência histórica. As dependências ativas estão definidas no `pyproject.toml`.

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

Para construir e publicar em uma única operação:

```bash
make build-and-push
```

## Validação

Antes de construir a imagem, você pode validar a configuração:

```bash
poetry run validate-config
```

E verificar se o Docker está configurado corretamente:

```bash
validate-docker
```

## Comandos disponíveis

Atualmente o projeto está em transição do Makefile para Poetry. O Makefile serve como uma camada de transição, onde os comandos `make` são aliases para os comandos Poetry correspondentes.

### Comandos via Make (aliases)

- `make config` - Alias para `poetry run config`
- `make config-ci` - Alias para `poetry run config-ci`
- `make build` - Alias para `poetry run build`
- `make push-image` - Alias para `poetry run push`
- `make build-and-push` - Alias para `poetry run build-and-push`
- `make validate-docker` - Alias para `poetry run validate-docker`
- `make validate-config` - Alias para `poetry run validate-config`

### Comandos diretos via Poetry

Todos os comandos também podem ser executados diretamente via Poetry:

- `poetry run config` - Configuração interativa
- `poetry run config-ci` - Commit das configurações atuais
- `poetry run build` - Construir imagem Docker
- `poetry run push` - Publicar imagem no Docker Hub
- `poetry run build-and-push` - Construir e publicar
- `poetry run validate-docker` - Validar instalação Docker
- `poetry run validate-config` - Validar configurações

