.PHONY: build push config config-ci

include config.mk

build: ## Constrói a imagem Docker conforme parâmetros contidos no arquivo config.mk
	docker buildx build \
		--tag $(DOCKER_IMAGE):$(DOCKER_TAG) \
		--secret id=secret,src=.env \
		--build-arg relatorios_version=$(RELATORIOS_VERSION) \
		--build-arg execucao_version=$(EXECUCAO_VERSION) \
		--build-arg reest_version=$(REEST_VERSION) \
		--build-arg ano_loa=$(ANO_LOA) \
		--build-arg docker_tag=$(DOCKER_TAG) \
		--build-arg docker_user=$(DOCKER_USER) \
		--build-arg docker_image=$(DOCKER_IMAGE) \
		.

push-image: 
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG)

config: ## Configura interativamente as variáveis do do arquivoconfig.mk
	@python3 scripts/config.py || true

config-ci: ## Executa apenas a parte de commit para as alterações no config.mk
	python3 scripts/config.py --commit-only