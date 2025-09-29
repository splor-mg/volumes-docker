.PHONY: build push config config-ci validate-docker validate-config build-and-push pacotes-check-version

include config.mk

install: ## Instala as dependências do projeto
	poetry install

build: ## Constrói a imagem Docker conforme parâmetros contidos no arquivo config.mk
	poetry run build

push-image: ## Faz push da imagem Docker para o Docker Hub
	poetry run push

config: ## Configura interativamente as variáveis do do arquivoconfig.mk
	@poetry run config || true

config-ci: ## Executa apenas a parte de commit para as alterações no config.mk
	poetry run config-ci

validate-docker: ## Valida configuração do Docker e dependências
	poetry run validate-docker

validate-config: ## Valida configurações do config.mk
	poetry run validate-config

build-push: ## Constrói e faz push da imagem Docker
	poetry run build-push

pacotes-check-version: ## Verifica e atualiza versões dos pacotes DCAF
	poetry run pacotes-check-version || true