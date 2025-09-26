#!/usr/bin/env python3
"""
Script para fazer push da imagem Docker para o Docker Hub
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

def check_image_exists(image_name, tag):
    """Verifica se a imagem existe localmente"""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", f"{image_name}:{tag}"],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def check_docker_login():
    """Verifica se o usuário está logado no Docker Hub"""
    try:
        result = subprocess.run(
            ["docker", "system", "info"],
            capture_output=True,
            text=True,
            check=True
        )
        return "Username:" in result.stdout
    except subprocess.CalledProcessError:
        return False

def tag_image(config):
    """Cria tag da imagem para o Docker Hub"""
    local_image = f"{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
    hub_image = f"{config['DOCKER_USER']}/{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
    
    print(f"🏷️  Criando tag: {local_image} -> {hub_image}")
    
    try:
        subprocess.run(["docker", "tag", local_image, hub_image], check=True)
        print("✅ Tag criada com sucesso!")
        return hub_image
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar tag: {e}")
        return None

def push_image(hub_image, verbose=False):
    """Faz push da imagem para o Docker Hub"""
    print(f"📤 Fazendo push da imagem: {hub_image}")
    
    if verbose:
        print("🔍 Comando executado:")
        print(f"docker push {hub_image}")
        print()
    
    try:
        subprocess.run(["docker", "push", hub_image], check=True)
        print("✅ Push concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no push: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Faz push da imagem Docker")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verboso")
    args = parser.parse_args()
    
    try:
        # Carregar configurações
        config = load_config()
        
        local_image = f"{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
        
        # Verificar se a imagem existe
        if not check_image_exists(config['DOCKER_IMAGE'], config['DOCKER_TAG']):
            print(f"❌ Imagem {local_image} não encontrada localmente")
            print("💡 Execute 'poetry run build' primeiro")
            sys.exit(1)
        
        # Verificar login no Docker Hub
        if not check_docker_login():
            print("⚠️  Você não está logado no Docker Hub")
            print("💡 Execute 'docker login' primeiro")
            sys.exit(1)
        
        # Criar tag
        hub_image = tag_image(config)
        if not hub_image:
            sys.exit(1)
        
        # Fazer push
        success = push_image(hub_image, args.verbose)
        
        if success:
            print(f"\n🎉 Imagem {hub_image} enviada com sucesso!")
            print("🌐 Acesse: https://hub.docker.com/r/{}/{}".format(
                config['DOCKER_USER'], 
                config['DOCKER_IMAGE']
            ))
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Push cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
