# =============================================================================
# CONFIGURAÇÕES DO PROJETO VOLUMES-DOCKER
# =============================================================================
# ATENÇÃO: Este arquivo é gerado automaticamente pelo comando 'make config'
# NÃO edite este arquivo manualmente - use 'make config' para modificá-lo
# Este arquivo deve ser versionado e atualizado a cada nova versão
# Última atualização: 2025-09-25 (commit: 46c8cba)
# =============================================================================

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
# Ano da LOA (Lei Orçamentária Anual)
# Exemplo: 2025 -> para LOA que entrará em vigor em 2025
ANO_LOA=2026

# =============================================================================
# CONFIGURAÇÕES DOCKER
# =============================================================================
# Tag da imagem Docker (versão)
# Formato: ploa{ANO} ou ploa{ANO}.{PATCH}
# Exemplos: ploa2025, ploa2025.1, ploa2025.2
DOCKER_TAG=ploa2026

# Usuário do Docker Hub
# Repositório: https://hub.docker.com/u/aidsplormg
DOCKER_USER=aidsplormg

# Nome da imagem Docker
# Imagem completa: aidsplormg/volumes
DOCKER_IMAGE=volumes

# =============================================================================
# VERSÕES DOS PACOTES R
# =============================================================================
# Relatórios - Pacote principal para geração de relatórios
# Exemplos: v0.7.99, v0.7.100
RELATORIOS_VERSION=v0.7.99

# Execução - Pacote para execução de processos
# Exemplos: v0.5.27, v0.5.28
EXECUCAO_VERSION=v0.5.27

# Reestruturação - Pacote para reestruturação de dados
# Exemplos: v0.2.8, v0.2.9
REEST_VERSION=v0.2.8

