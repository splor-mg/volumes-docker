#!/usr/bin/env python3
"""
Script para validar configurações do config.mk
"""

import sys
from pathlib import Path

def load_config():
    """Carrega variáveis do config.mk"""
    config = {}
    config_file = Path("config.mk")
    
    if not config_file.exists():
        print("❌ Arquivo config.mk não encontrado")
        return None
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config

def validate_required_vars(config):
    """Valida variáveis obrigatórias"""
    required_vars = [
        'DOCKER_IMAGE',
        'DOCKER_TAG', 
        'DOCKER_USER',
        'RELATORIOS_VERSION',
        'EXECUCAO_VERSION',
        'REEST_VERSION',
        'ANO_LOA'
    ]
    
    missing = []
    for var in required_vars:
        if var not in config or not config[var]:
            missing.append(var)
    
    if missing:
        print("❌ Variáveis obrigatórias ausentes:")
        for var in missing:
            print(f"   • {var}")
        return False
    
    print("✅ Todas as variáveis obrigatórias estão definidas")
    return True

def validate_docker_vars(config):
    """Valida variáveis específicas do Docker"""
    issues = []
    
    # Validar DOCKER_TAG (deve ser alfanumérico com hífens)
    if not config['DOCKER_TAG'].replace('-', '').replace('.', '').isalnum():
        issues.append("DOCKER_TAG deve conter apenas letras, números, hífens e pontos")
    
    # Validar DOCKER_USER (deve ser alfanumérico com hífens)
    if not config['DOCKER_USER'].replace('-', '').isalnum():
        issues.append("DOCKER_USER deve conter apenas letras, números e hífens")
    
    # Validar ANO_LOA (deve ser um ano válido)
    try:
        year = int(config['ANO_LOA'])
        if year < 2020 or year > 2030:
            issues.append("ANO_LOA deve ser um ano entre 2020 e 2030")
    except ValueError:
        issues.append("ANO_LOA deve ser um número")
    
    if issues:
        print("❌ Problemas nas variáveis do Docker:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    print("✅ Variáveis do Docker estão válidas")
    return True

def validate_version_vars(config):
    """Valida variáveis de versão"""
    version_vars = ['RELATORIOS_VERSION', 'EXECUCAO_VERSION', 'REEST_VERSION']
    
    for var in version_vars:
        value = config[var]
        if not value or value == 'latest':
            print(f"⚠️  {var} está definida como '{value}' (considere usar uma versão específica)")
        else:
            print(f"✅ {var}: {value}")
    
    return True

def print_config_summary(config):
    """Imprime resumo da configuração"""
    print("\n📋 Resumo da configuração:")
    print("-" * 30)
    print(f"🐳 Imagem: {config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}")
    print(f"👤 Usuário: {config['DOCKER_USER']}")
    print(f"📅 Ano LOA: {config['ANO_LOA']}")
    print(f"📦 Relatórios: {config['RELATORIOS_VERSION']}")
    print(f"📦 Execução: {config['EXECUCAO_VERSION']}")
    print(f"📦 Reest: {config['REEST_VERSION']}")

def main():
    """Função principal"""
    print("🔍 Validando configuração do config.mk...")
    print("=" * 40)
    
    # Carregar configuração
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Validar variáveis obrigatórias
    if not validate_required_vars(config):
        sys.exit(1)
    
    # Validar variáveis do Docker
    if not validate_docker_vars(config):
        sys.exit(1)
    
    # Validar variáveis de versão
    validate_version_vars(config)
    
    # Imprimir resumo
    print_config_summary(config)
    
    print("\n🎉 Configuração válida!")
    print("💡 Você está pronto para usar 'poetry run build'")

if __name__ == "__main__":
    main()
