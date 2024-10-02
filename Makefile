.PHONY: build

build: 
	docker buildx build \
    --tag volumes:$(image) \
    --secret id=secret,src=.env \
    --build-arg relatorios_version=$(relatorios) \
    --build-arg execucao_version=$(execucao) \
    --build-arg reest_version=$(reest) \
    .