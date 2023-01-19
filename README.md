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
make volume=ploa2023 relatorios=v0.6.87 execucao=v0.5.16
```

O valor do argumento `volume` vai ser utilizado para taguear a imagem.
