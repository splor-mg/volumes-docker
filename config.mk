# config.mk - Configurações do projeto volumes-docker
# Este arquivo deve ser versionado e atualizado a cada nova versão

# Ano da LOA (Lei Orçamentária Anual)
# Exemplo: 2025 -> para LOA que entrará em vigor em 2025
ANO_LOA=2025

# Tag da imagem Docker (versão)
DOCKER_TAG=ploa2025 # ex.1.: ploa2025 ex.2.: ploa2025.1 

# Usuário do Docker Hub (por padrão: aidsplormg, https://hub.docker.com/u/aidsplormg)
DOCKER_USER=aidsplormg

# Nome da imagem Docker (por padrão: volumes, https://hub.docker.com/r/aidsplormg/volumes)
DOCKER_IMAGE=volumes

# Versões dos pacotes R
RELATORIOS_VERSION=v0.7.99 # ex.: v0.7.64
EXECUCAO_VERSION=v0.5.27 # ex.: v0.5.22
REEST_VERSION=v0.2.8 # ex.: v0.2.6

# Histórico de versões (para referência)
# LOA 2024:
# DOCKER_TAG=ploa2024
# RELATORIOS_VERSION=v0.6.39
# EXECUCAO_VERSION=v0.5.7
# REEST_VERSION=v0.2.5
