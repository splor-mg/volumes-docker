#!/usr/bin/env python3
"""
Script para construir e fazer push da imagem Docker
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_script(script_name, args=None):
    """Executa um script Python"""
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)]
    
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar {script_name}: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Constrói e faz push da imagem Docker")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verboso")
    args = parser.parse_args()
    
    print("🚀 Iniciando build e push da imagem Docker...")
    print("=" * 50)
    
    # Argumentos para passar para os scripts
    script_args = []
    if args.verbose:
        script_args.append("--verbose")
    
    try:
        # 1. Build da imagem
        print("📦 ETAPA 1: Build da imagem")
        print("-" * 30)
        if not run_script("docker_build.py", script_args):
            print("❌ Build falhou. Abortando push.")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        
        # 2. Push da imagem
        print("📤 ETAPA 2: Push da imagem")
        print("-" * 30)
        if not run_script("docker_push.py", script_args):
            print("❌ Push falhou.")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("🎉 Build e push concluídos com sucesso!")
        print("💡 A imagem está disponível no Docker Hub")
        
    except KeyboardInterrupt:
        print("\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
