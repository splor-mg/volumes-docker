#!/usr/bin/env python3
"""
Script interativo para configurar o config.mk
"""

import os
import re
import sys
import subprocess
from pathlib import Path

# Cores para output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("Configurando volumes-docker...")
    print("=" * 40)
    print(f"{Colors.END}")

def read_config_file():
    """Lê o arquivo config.mk atual e extrai os valores"""
    config_path = Path("config.mk")
    values = {}
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove comentários inline
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    values[key] = value
    
    return values

def validate_version(version):
    """Valida se a versão começa com 'v'"""
    return version.startswith('v') and len(version) > 1

def validate_ano_loa(ano):
    """Valida se o ano é um número de 4 dígitos"""
    return ano.isdigit() and len(ano) == 4

def validate_docker_tag(tag):
    """Valida se a tag do Docker é válida"""
    # Tag deve conter apenas letras, números, pontos, hífens e underscores
    return re.match(r'^[a-zA-Z0-9._-]+$', tag) is not None

def get_user_input(prompt, current_value, validator=None):
    """Pede input do usuário com valor padrão e validação"""
    while True:
        if current_value:
            user_input = input(f"{prompt}: [{current_value}] ").strip()
            if not user_input:
                user_input = current_value
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input:
            print(f"{Colors.RED}Este campo é obrigatório!{Colors.END}")
            continue
            
        if validator and not validator(user_input):
            print(f"{Colors.RED}Formato inválido!{Colors.END}")
            continue
            
        return user_input

def show_preview(new_values):
    """Mostra preview das configurações antes de salvar"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}Preview das configurações:{Colors.END}")
    print("-" * 40)
    for key, value in new_values.items():
        print(f"{key:20} = {value}")
    print("-" * 40)

def save_config(values):
    """Salva as configurações no config.mk"""
    config_content = f"""# config.mk - Configurações do projeto volumes-docker
# Este arquivo deve ser versionado e atualizado a cada nova versão

# Ano da LOA (Lei Orçamentária Anual)
# Exemplo: 2025 -> para LOA que entrará em vigor em 2025
ANO_LOA={values['ANO_LOA']}

# Tag da imagem Docker (versão)
DOCKER_TAG={values['DOCKER_TAG']} # ex.1.: ploa2025 ex.2.: ploa2025.1 

# Usuário do Docker Hub (por padrão: aidsplormg, https://hub.docker.com/u/aidsplormg)
DOCKER_USER={values['DOCKER_USER']}

# Nome da imagem Docker (por padrão: volumes, https://hub.docker.com/r/aidsplormg/volumes)
DOCKER_IMAGE={values['DOCKER_IMAGE']}

# Versões dos pacotes R
RELATORIOS_VERSION={values['RELATORIOS_VERSION']} # ex.: v0.7.64
EXECUCAO_VERSION={values['EXECUCAO_VERSION']} # ex.: v0.5.22
REEST_VERSION={values['REEST_VERSION']} # ex.: v0.2.6

# Histórico de versões (para referência)
# LOA 2024:
# DOCKER_TAG=ploa2024
# RELATORIOS_VERSION=v0.6.39
# EXECUCAO_VERSION=v0.5.7
# REEST_VERSION=v0.2.5
"""
    
    with open("config.mk", 'w') as f:
        f.write(config_content)


def get_commit_info():
    """Coleta informações para o commit"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Configuração de Commit{Colors.END}")
    print("-" * 30)
    
    # Git add
    add_confirm = input("git add config.mk (Y/n): ").strip().lower()
    if add_confirm in ['n', 'no']:
        return None
    
    # Issue information
    print(f"\n{Colors.YELLOW}qual issue?{Colors.END}")
    org = input('org: "splor-mg" [splor-mg]: ').strip() or 'splor-mg'
    repo = input('repo: "volumes-docker" [volumes-docker]: ').strip() or 'volumes-docker'
    number = input('number: [opcional]: ').strip()
    
    return {
        'org': org,
        'repo': repo,
        'number': number
    }

def build_commit_message(values, commit_info):
    """Constrói a mensagem de commit"""
    # Monta o link do issue se fornecido
    issue_link = ""
    if commit_info['number']:
        issue_link = f"\nSee https://github.com/{commit_info['org']}/{commit_info['repo']}/issues/{commit_info['number']}"
    
    # Monta os parâmetros na ordem do config.mk
    params = []
    param_order = ['ANO_LOA', 'DOCKER_TAG', 'DOCKER_USER', 'DOCKER_IMAGE', 
                   'RELATORIOS_VERSION', 'EXECUCAO_VERSION', 'REEST_VERSION']
    
    for param in param_order:
        if param in values:
            params.append(f"  {param.lower()}: {values[param]}")
    
    params_text = "\n".join(params)
    
    commit_message = f"""chore(config): update ano_loa {values['ANO_LOA']}{issue_link}

Demais parâmetros:
{params_text}"""
    
    return commit_message

def show_commit_preview(commit_message):
    """Mostra preview da mensagem de commit"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}Preview da mensagem de commit:{Colors.END}")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)

def make_commit(commit_message):
    """Executa o commit"""
    try:
        # Git add
        subprocess.run(['git', 'add', 'config.mk'], check=True)
        
        # Git commit
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}Commit realizado com sucesso!{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.RED}Erro ao fazer commit: {e}{Colors.END}")
        return False

def main():
    # Verifica se é modo commit-only
    commit_only = '--commit-only' in sys.argv
    
    if commit_only:
        print(f"{Colors.BLUE}{Colors.BOLD}Modo Commit-Only{Colors.END}")
        print("=" * 40)
        print(f"{Colors.END}")
    
    print_header()
    
    # Lê valores atuais
    current_values = read_config_file()
    
    # Define valores padrão se não existirem
    defaults = {
        'ANO_LOA': '2025',
        'DOCKER_TAG': 'ploa2025',
        'DOCKER_USER': 'aidsplormg',
        'DOCKER_IMAGE': 'volumes',
        'RELATORIOS_VERSION': 'v0.7.64',
        'EXECUCAO_VERSION': 'v0.5.22',
        'REEST_VERSION': 'v0.2.6'
    }
    
    # Mescla valores atuais com padrões
    for key, default_value in defaults.items():
        if key not in current_values:
            current_values[key] = default_value
    
    if not commit_only:
        # Coleta inputs do usuário
        new_values = {}
        
        print("Configure as variáveis do projeto:")
        print(f"{Colors.YELLOW}(Pressione Enter para aceitar o valor padrão ou digite o valor correto){Colors.END}\n")
        
        new_values['ANO_LOA'] = get_user_input(
            "Ano da LOA", 
            current_values.get('ANO_LOA'), 
            validate_ano_loa
        )
        
        new_values['DOCKER_TAG'] = get_user_input(
            "Tag da imagem Docker", 
            current_values.get('DOCKER_TAG'), 
            validate_docker_tag
        )
        
        new_values['DOCKER_USER'] = get_user_input(
            "Usuário do Docker Hub", 
            current_values.get('DOCKER_USER')
        )
        
        new_values['DOCKER_IMAGE'] = get_user_input(
            "Nome da imagem Docker", 
            current_values.get('DOCKER_IMAGE')
        )
        
        new_values['RELATORIOS_VERSION'] = get_user_input(
            "Versão do pacote relatorios", 
            current_values.get('RELATORIOS_VERSION'), 
            validate_version
        )
        
        new_values['EXECUCAO_VERSION'] = get_user_input(
            "Versão do pacote execucao", 
            current_values.get('EXECUCAO_VERSION'), 
            validate_version
        )
        
        new_values['REEST_VERSION'] = get_user_input(
            "Versão do pacote reest", 
            current_values.get('REEST_VERSION'), 
            validate_version
        )
        
        # Mostra preview
        show_preview(new_values)
        
        # Confirmação
        confirm = input(f"\n{Colors.YELLOW}Salvar configurações? (y/N): {Colors.END}").strip().lower()
        
        if confirm in ['y', 'yes', 's', 'sim']:
            save_config(new_values)
            print(f"\n{Colors.GREEN}{Colors.BOLD}Configuração salva em config.mk!{Colors.END}")
        else:
            print(f"\n{Colors.RED}Configuração cancelada.{Colors.END}")
            sys.exit(1)
    else:
        # Modo commit-only: usa valores atuais do config.mk
        new_values = current_values
        print(f"{Colors.GREEN}Usando configurações atuais do config.mk{Colors.END}")
    
    # Pergunta se quer fazer commit
    commit_choice = input(f"\n{Colors.YELLOW}Quer fazer commit das alterações? (Y/n): {Colors.END}").strip().lower()
    
    if commit_choice not in ['n', 'no']:
        commit_info = get_commit_info()
        if commit_info:
            commit_message = build_commit_message(new_values, commit_info)
            show_commit_preview(commit_message)
            
            commit_confirm = input(f"\n{Colors.YELLOW}Fazer commit? (Y/n): {Colors.END}").strip().lower()
            if commit_confirm not in ['n', 'no']:
                make_commit(commit_message)
            else:
                print(f"\n{Colors.RED}Commit cancelado.{Colors.END}")
        else:
            print(f"\n{Colors.RED}Commit cancelado.{Colors.END}")
    else:
        print(f"\n{Colors.BLUE}Commit não solicitado.{Colors.END}")

if __name__ == "__main__":
    main()
