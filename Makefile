.PHONY: build

build: 
	docker build \
    --tag volumes:$(volume) \
    --secret id=secret,src=.env \
    --build-arg relatorios_version=$(relatorios) \
    --build-arg execucao_version=$(execucao) \
    .