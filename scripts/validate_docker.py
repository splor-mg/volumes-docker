#!/usr/bin/env python3
"""
Script para validar configuração do Docker e dependências
"""

import os
import sys
import subprocess
from pathlib import Path

def check_docker_installed():
    """Verifica se o Docker está instalado"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Docker instalado: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker não está instalado")
        return False

def check_docker_running():
    """Verifica se o Docker está rodando"""
    try:
        subprocess.run(["docker", "version"], capture_output=True, check=True)
        print("✅ Docker está rodando")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker não está rodando")
        print("💡 Inicie o Docker e tente novamente")
        return False

def check_docker_login():
    """Verifica se está logado no Docker Hub"""
    try:
        result = subprocess.run(["docker", "system", "info"], capture_output=True, text=True, check=True)
        if "Username:" in result.stdout:
            print("✅ Logado no Docker Hub")
            return True
        else:
            print("⚠️  Não está logado no Docker Hub")
            print("💡 Execute 'docker login' para fazer login")
            return False
    except subprocess.CalledProcessError:
        print("❌ Erro ao verificar login no Docker Hub")
        return False

def check_config_file():
    """Verifica se o arquivo config.mk existe"""
    if Path("config.mk").exists():
        print("✅ Arquivo config.mk encontrado")
        return True
    else:
        print("❌ Arquivo config.mk não encontrado")
        print("💡 Execute 'poetry run config' para criar")
        return False

def check_env_file():
    """Verifica se o arquivo .env existe"""
    if Path(".env").exists():
        print("✅ Arquivo .env encontrado")
        return True
    else:
        print("❌ Arquivo .env não encontrado")
        print("💡 Crie o arquivo .env com suas credenciais")
        return False

def check_docker_buildx():
    """Verifica se o Docker Buildx está disponível"""
    try:
        result = subprocess.run(["docker", "buildx", "version"], capture_output=True, text=True, check=True)
        print("✅ Docker Buildx disponível")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker Buildx não está disponível")
        print("💡 Atualize o Docker para uma versão mais recente")
        return False

def main():
    """Função principal"""
    print("🔍 Validando configuração do Docker...")
    print("=" * 40)
    
    checks = [
        ("Docker instalado", check_docker_installed),
        ("Docker rodando", check_docker_running),
        ("Docker Buildx", check_docker_buildx),
        ("Arquivo config.mk", check_config_file),
        ("Arquivo .env", check_env_file),
        ("Login Docker Hub", check_docker_login),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n🔍 {name}:")
        if check_func():
            passed += 1
        else:
            print(f"   ❌ Falha na verificação: {name}")
    
    print("\n" + "=" * 40)
    print(f"📊 Resultado: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("🎉 Todas as verificações passaram!")
        print("💡 Você está pronto para usar 'poetry run build' e 'poetry run push'")
        sys.exit(0)
    else:
        print("⚠️  Algumas verificações falharam")
        print("💡 Resolva os problemas acima e execute novamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
