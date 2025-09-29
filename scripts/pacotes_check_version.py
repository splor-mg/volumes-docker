#!/usr/bin/env python3
"""
Verifica as versões mais recentes dos pacotes DCAF (relatorios, execucao, reest)
na organização splor-mg e atualiza o arquivo config.mk deste projeto, se necessário.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import requests


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def load_config() -> dict:
    config_file = Path("config.mk")
    if not config_file.exists():
        print(f"{Colors.RED}❌ Arquivo config.mk não encontrado{Colors.END}")
        sys.exit(1)

    config: dict = {}
    with open(config_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

def load_env_file() -> None:
    """Carrega variáveis do arquivo .env, se existir (sem dependência externa)."""
    env_path = Path('.env')
    if not env_path.exists():
        return
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Silencioso de propósito
        pass


def get_latest_release(repo_name: str) -> str:
    releases_url = f"https://api.github.com/repos/splor-mg/{repo_name}/releases/latest"
    tags_url = f"https://api.github.com/repos/splor-mg/{repo_name}/tags"

    headers = {"User-Agent": "volumes-docker-version-check/1.0"}
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_PAT')
    if token:
        headers['Authorization'] = f'token {token}'

    # Tenta releases
    try:
        resp = requests.get(releases_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            tag = resp.json().get('tag_name', '')
        else:
            # Fallback para tags
            if resp.status_code in (403, 401):
                try:
                    msg = resp.json().get('message', '')
                except Exception:
                    msg = ''
                print(f"{Colors.YELLOW}⚠️  Acesso a releases de {repo_name} falhou (status {resp.status_code}). {msg}{Colors.END}")

            resp = requests.get(tags_url, headers=headers, timeout=15)
            if resp.status_code == 200 and resp.json():
                tag = resp.json()[0].get('name', '')
            else:
                if resp.status_code != 200:
                    try:
                        msg = resp.json().get('message', '')
                    except Exception:
                        msg = ''
                    print(f"{Colors.YELLOW}⚠️  Falha ao obter tags de {repo_name} (status {resp.status_code}). {msg}{Colors.END}")
                return None

        if tag and not tag.startswith('v'):
            tag = f"v{tag}"
        return tag or None
    except requests.RequestException as e:
        print(f"{Colors.YELLOW}⚠️  Erro de rede ao consultar {repo_name}: {e}{Colors.END}")
        return None


def update_config_mk(updates: dict) -> bool:
    config_file = Path("config.mk")
    lines = config_file.read_text(encoding="utf-8").splitlines(True)

    changed = False
    for package, new_version in updates.items():
        var = f"{package.upper()}_VERSION"
        for idx, line in enumerate(lines):
            if line.startswith(f"{var}="):
                old_value = line.split('=', 1)[1].strip()
                if old_value != new_version:
                    lines[idx] = f"{var}={new_version}\n"
                    print(f"📝 {var}: {old_value} → {new_version}")
                    changed = True
                break

    if changed:
        # Atualiza carimbo de data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i, line in enumerate(lines):
            if line.startswith("# Última atualização:"):
                lines[i] = f"# Última atualização: {timestamp} (auto-update)\n"
                break

        config_file.write_text(''.join(lines), encoding="utf-8")
        print(f"{Colors.GREEN}✅ config.mk atualizado com sucesso!{Colors.END}")
        return True

    print(f"{Colors.BLUE}ℹ️  Nenhuma atualização necessária{Colors.END}")
    return False


def check_package_versions() -> bool:
    # Cabeçalho
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("📦 VERIFICAÇÃO DE VERSÕES DOS PACOTES DCAF")
    print("   VOLUMES-DOCKER")
    print("=" * 60)
    print(f"{Colors.END}")

    # Token
    has_token = bool(os.getenv('GITHUB_TOKEN') or os.getenv('GH_PAT'))
    if has_token:
        print("🔑 Usando token do GitHub para acessar repositórios privados")
    else:
        print("⚠️  GITHUB_TOKEN não encontrado - repositórios privados podem não ser acessíveis")
    print()

    packages = {
        'relatorios': 'RELATORIOS_VERSION',
        'execucao': 'EXECUCAO_VERSION',
        'reest': 'REEST_VERSION',
    }

    print("🔍 Verificando versões no GitHub...\n")

    updates: dict = {}
    errors: list = []
    config = load_config()

    for repo, var in packages.items():
        current = config.get(var, 'NÃO_DEFINIDO')
        print(f"📦 {repo}:")
        print(f"   Atual: {current}")

        latest = get_latest_release(repo)
        if latest:
            print(f"   GitHub: {latest}")
            if current != latest:
                updates[repo] = latest
                print(f"   {Colors.YELLOW}🔄 Atualização disponível!{Colors.END}")
            else:
                print(f"   {Colors.GREEN}✅ Já está atualizado{Colors.END}")
        else:
            print(f"   {Colors.RED}❌ Não foi possível obter versão{Colors.END}")
            errors.append(repo)
        print()

    if errors:
        print(f"{Colors.YELLOW}⚠️  Não foi possível verificar: {', '.join(errors)}{Colors.END}")
        if not has_token:
            print(f"{Colors.BLUE}💡 Dica: configure GITHUB_TOKEN ou GH_PAT para acessar repositórios privados{Colors.END}")
        print()

    if updates:
        print("🔧 Atualizando config.mk...")
        updated = update_config_mk(updates)
        if updated:
            print(f"\n{Colors.GREEN}🎉 Atualizações aplicadas com sucesso!{Colors.END}")
            print(f"📋 Pacotes atualizados: {', '.join(updates.keys())}")
            return True
        else:
            print(f"\n{Colors.RED}❌ Erro ao atualizar config.mk{Colors.END}")
            return False

    if errors and not updates:
        print(f"{Colors.YELLOW}ℹ️  Nenhuma atualização possível devido a erros de acesso{Colors.END}")
        return False

    print(f"{Colors.BLUE}ℹ️  Todos os pacotes verificados já estão atualizados{Colors.END}")
    return False


def main():
    try:
        # Carrega .env (GITHUB_TOKEN/GH_PAT) se existir
        load_env_file()
        changed = check_package_versions()
        if changed:
            sys.exit(0)
        else:
            sys.exit(1)  # Sem mudanças
    except Exception as e:
        print(f"{Colors.RED}❌ Erro: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()


