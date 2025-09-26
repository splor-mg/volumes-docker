#!/usr/bin/env python3
"""
Script para construir imagem Docker conforme parâmetros do config.mk
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def load_config():
    """Carrega variáveis do config.mk"""
    config = {}
    config_file = Path("config.mk")
    
    if not config_file.exists():
        print("❌ Arquivo config.mk não encontrado")
        print("💡 Execute 'poetry run config' primeiro")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config

def validate_environment():
    """Valida se o ambiente está configurado corretamente"""
    errors = []
    
    # Verificar se .env existe
    if not Path(".env").exists():
        errors.append("Arquivo .env não encontrado")
    
    # Verificar se Docker está rodando
    try:
        subprocess.run(["docker", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("Docker não está rodando ou não está instalado")
    
    if errors:
        print("❌ Problemas encontrados:")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 Resolva os problemas acima e tente novamente")
        sys.exit(1)

def build_docker_image(config, verbose=False):
    """Constrói a imagem Docker"""
    print("🔨 Iniciando build da imagem Docker...")
    print(f"📦 Imagem: {config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}")
    print(f"👤 Usuário: {config['DOCKER_USER']}")
    print(f"📅 Ano LOA: {config['ANO_LOA']}")
    print()
    
    # Comando docker buildx build
    cmd = [
        "docker", "buildx", "build",
        "--tag", f"{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}",
        "--secret", "id=secret,src=.env",
        "--build-arg", f"relatorios_version={config['RELATORIOS_VERSION']}",
        "--build-arg", f"execucao_version={config['EXECUCAO_VERSION']}",
        "--build-arg", f"reest_version={config['REEST_VERSION']}",
        "--build-arg", f"ano_loa={config['ANO_LOA']}",
        "--build-arg", f"docker_tag={config['DOCKER_TAG']}",
        "--build-arg", f"docker_user={config['DOCKER_USER']}",
        "--build-arg", f"docker_image={config['DOCKER_IMAGE']}",
        "."
    ]
    
    if verbose:
        print("🔍 Comando executado:")
        print(" ".join(cmd))
        print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Build concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Constrói imagem Docker")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verboso")
    args = parser.parse_args()
    
    try:
        # Validar ambiente
        validate_environment()
        
        # Carregar configurações
        config = load_config()
        
        # Construir imagem
        success = build_docker_image(config, args.verbose)
        
        if success:
            print(f"\n🎉 Imagem {config['DOCKER_IMAGE']}:{config['DOCKER_TAG']} construída com sucesso!")
            print("💡 Use 'poetry run push' para fazer push da imagem")
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Build cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
