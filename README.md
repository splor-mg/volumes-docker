# Docker para geração dos volumes das leis orçamentárias

## Pré-requisitos

Os segredos (token do GitHub para instalar os pacotes privados, usuário e
[access token](https://hub.docker.com/settings/security) do Docker Hub, nome
da imagem) são gerenciados no [Infisical](https://infisical.com/),
não em um arquivo `.env` local. É necessário ter o [Infisical CLI](https://infisical.com/docs/cli/overview)
instalado e autenticado (`infisical login`) para o projeto já configurado neste
repositório (`.infisical.json`).

Todos os comandos abaixo devem ser prefixados com `infisical run --`, que
injeta os segredos como variáveis de ambiente para o comando executado, por
exemplo:

```bash
infisical run -- make build base=1 relatorios=v0.8.01.1 execucao=v0.5.27 reest=v0.2.8
```

## Estrutura das imagens

O processo é dividido em duas imagens (ver [ADR 0001](docs/adr/0001-split-base-and-app-images.md)):

- **Imagem base** (`base/Dockerfile`) — sistema operacional, R, Python
  compilado, `diff-pdf`/`diff-so-fancy`, TeX. Muda raramente, é construída e
  publicada manualmente.
- **Imagem da aplicação** (`Dockerfile` na raiz) — parte a partir da imagem
  base e instala as dependências Python via Poetry e os três pacotes privados
  `relatorios`, `execucao`, `reest`. É a imagem construída a cada release.

## Construção da imagem base

Bump da imagem base é uma decisão manual e pouco frequente:

```bash
infisical run -- make build-base n=2 push=1
```

## Construção da imagem da aplicação

Para construir a imagem passando as versões manualmente:

```bash
infisical run -- make build base=1 relatorios=v0.8.01.1 execucao=v0.5.27 reest=v0.2.8 push=1
```

Omitir `push=1` para apenas construir a imagem localmente, sem publicar.

## Checagem e build automático de atualizações

Para checar se há novas versões de `relatorios`, `execucao` ou `reest` no
GitHub em relação ao que está publicado na tag `latest` do Docker Hub:

```bash
infisical run -- make check-updates
```

Para checar e, se houver atualização, construir e publicar automaticamente:

```bash
infisical run -- make release
```

Esse é o mesmo comando executado diariamente pela Action
[`publish_image.yaml`](.github/workflows/publish_image.yaml).

## Publicação da imagem no Docker Hub

Nome de usuário, access token e nome da imagem no Docker Hub vêm do Infisical
(`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `DOCKERHUB_IMAGE_NAME`) — não estão
hardcoded nos scripts, então mudanças nesses valores não exigem alteração de
código. O login e o push já acontecem como parte de `make build push=1` /
`make build-base push=1` / `make release`, não é um passo manual separado.
