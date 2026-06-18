"""
setup_github.py -- Automatizacion de configuracion de repositorio GitHub
para el proyecto: 2026-06-16-RAG-Industrial (Estructura Python + CI)

Requisitos:
    pip install PyGithub

Uso:
    python setup_github.py
"""

import os
import subprocess
from pathlib import Path

# --- Importaciones con manejo de errores claros --------------------------------
try:
    from github import Github, GithubException, Auth
except ImportError:
    raise SystemExit("[ERROR] Falta la libreria PyGithub. Ejecuta: pip install PyGithub")

try:
    import requests
except ImportError:
    raise SystemExit("[ERROR] Falta la libreria requests. Ejecuta: pip install requests")

# ==============================================================================
#  SECCION DE CONFIGURACION -- Edita estos valores antes de ejecutar el script
# ==============================================================================

CONFIG = {
    # -- GitHub ----------------------------------------------------------------
    "GITHUB_TOKEN"      : os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN"),
    "GITHUB_USERNAME"   : "elproximoframework",
    "REPO_NAME"         : "2026-06-16-RAG-Industrial",
    "REPO_PRIVATE"      : False,   # False = publico (recomendado para que rulesets funcionen en plan Free)
    "REPO_DESCRIPTION"  : "Sistema RAG Industrial con Pipeline de Integracion Continua (CI)",

    # -- Rutas locales ---------------------------------------------------------
    "LOCAL_PROJECT_PATH": str(Path(__file__).parent),
}

# ==============================================================================
#  FUNCIONES AUXILIARES
# ==============================================================================

def run_git(cmd: list, cwd: str):
    """Ejecuta un comando git en el directorio indicado."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git error en '{' '.join(cmd)}':\n{result.stderr}")
    return result.stdout.strip()


def print_step(step: str, description: str):
    print(f"\n{'-' * 60}")
    print(f"[PASO {step}] {description}")
    print('-' * 60)


def print_ok(msg: str):
    print(f"  [OK]  {msg}")


def print_skip(msg: str):
    print(f"  [SKIP]   {msg} -- Omitido (ya existe)")


# ==============================================================================
#  PASO 1: Conectar con GitHub y crear el repositorio
# ==============================================================================

def create_repository(gh: Github) -> object:
    print_step("1", "Crear repositorio en GitHub")
    user = gh.get_user()

    try:
        repo = user.get_repo(CONFIG["REPO_NAME"])
        print_skip(f"Repositorio '{CONFIG['REPO_NAME']}' ya existe")
    except GithubException:
        repo = user.create_repo(
            name=CONFIG["REPO_NAME"],
            description=CONFIG["REPO_DESCRIPTION"],
            private=CONFIG["REPO_PRIVATE"],
            auto_init=False,
        )
        print_ok(f"Repositorio creado: {repo.html_url}")

    return repo


# ==============================================================================
#  PASO 2: Inicializar git y hacer el push inicial del proyecto
# ==============================================================================

def init_and_push(repo) -> None:
    print_step("2", "Inicializar Git y subir codigo inicial")

    project_path = CONFIG["LOCAL_PROJECT_PATH"]
    remote_url = f"https://{CONFIG['GITHUB_TOKEN']}@github.com/{CONFIG['GITHUB_USERNAME']}/{CONFIG['REPO_NAME']}.git"

    # Inicializar el repositorio local si no tiene .git
    git_dir = Path(project_path) / ".git"
    if not git_dir.exists():
        run_git(["git", "init"], cwd=project_path)
        run_git(["git", "config", "user.name", CONFIG["GITHUB_USERNAME"]], cwd=project_path)
        run_git(["git", "config", "user.email", f"{CONFIG['GITHUB_USERNAME']}@gmail.com"], cwd=project_path)
        print_ok("Repositorio local inicializado")
    else:
        print_skip("Repositorio local ya inicializado")

    # Asegurarse de que estamos en la rama main
    run_git(["git", "checkout", "-B", "main"], cwd=project_path)

    # Anadir remote si no existe
    try:
        run_git(["git", "remote", "add", "origin", remote_url], cwd=project_path)
        print_ok("Remote 'origin' configurado")
    except RuntimeError:
        run_git(["git", "remote", "set-url", "origin", remote_url], cwd=project_path)
        print_skip("Remote 'origin' actualizado")

    # Primer commit si no hay commits
    try:
        run_git(["git", "log", "--oneline", "-1"], cwd=project_path)
        print_skip("Ya existen commits en el repositorio local")
    except RuntimeError:
        run_git(["git", "add", "."], cwd=project_path)
        run_git(["git", "commit", "-m", "feat: initial project setup con estructura CI"], cwd=project_path)
        print_ok("Commit inicial creado en 'main'")

    # Push a main
    run_git(["git", "push", "-u", "origin", "main", "--force"], cwd=project_path)
    print_ok("Rama 'main' subida a GitHub")

    # Crear y subir rama dev
    run_git(["git", "checkout", "-B", "dev"], cwd=project_path)
    run_git(["git", "push", "-u", "origin", "dev", "--force"], cwd=project_path)
    print_ok("Rama 'dev' subida a GitHub")

    # Volver a main
    run_git(["git", "checkout", "main"], cwd=project_path)


# ==============================================================================
#  PASO 3: Configurar Rulesets (Branch Protection) para main y dev
# ==============================================================================

def setup_rulesets(repo) -> None:
    print_step("3", "Configurar Branch Protection Rulesets")

    headers = {
        "Authorization": f"Bearer {CONFIG['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    base_url = f"https://api.github.com/repos/{CONFIG['GITHUB_USERNAME']}/{CONFIG['REPO_NAME']}"
    
    # actor_id=5 = rol 'admin' del repositorio (no es el ID del usuario)
    actor_id = 5

    def build_ruleset_payload(branch_name: str) -> dict:
        return {
            "name": f"protect-{branch_name}",
            "target": "branch",
            "enforcement": "active",
            "bypass_actors": [
                {
                    "actor_id": actor_id,
                    "actor_type": "RepositoryRole",
                    "bypass_mode": "always"
                }
            ],
            "conditions": {
                "ref_name": {
                    "include": [f"refs/heads/{branch_name}"],
                    "exclude": []
                }
            },
            "rules": [
                {"type": "deletion"},
                {"type": "non_fast_forward"},
                {
                    "type": "pull_request",
                    "parameters": {
                        "required_approving_review_count": 1,
                        "dismiss_stale_reviews_on_push": False,
                        "require_code_owner_review": False,
                        "require_last_push_approval": False,
                        "required_review_thread_resolution": False
                    }
                }
            ]
        }

    # Eliminar rulesets existentes con el mismo nombre (idempotencia)
    r = requests.get(f"{base_url}/rulesets", headers=headers)
    if r.status_code == 200:
        for rs in r.json():
            if rs["name"] in ["protect-main", "protect-dev"]:
                requests.delete(f"{base_url}/rulesets/{rs['id']}", headers=headers)
                print_skip(f"Ruleset '{rs['name']}' eliminado para recrear")

    # Crear ruleset para main
    r = requests.post(f"{base_url}/rulesets", headers=headers, json=build_ruleset_payload("main"))
    if r.status_code in (200, 201):
        print_ok("Ruleset de proteccion para 'main' creado (Activo + Bypass para admin)")
    else:
        print(f"  WARNING Ruleset main: {r.status_code} -- {r.text[:200]}")

    # Crear ruleset para dev
    r = requests.post(f"{base_url}/rulesets", headers=headers, json=build_ruleset_payload("dev"))
    if r.status_code in (200, 201):
        print_ok("Ruleset de proteccion para 'dev' creado (Activo + Bypass para admin)")
    else:
        print(f"  WARNING Ruleset dev: {r.status_code} -- {r.text[:200]}")


# ==============================================================================
#  PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================

def main():
    print("\n" + "=" * 60)
    print("  SETUP AUTOMATICO -- Repositorio GitHub para RAG Industrial")
    print("=" * 60)

    # Conectar con GitHub
    auth = Auth.Token(CONFIG["GITHUB_TOKEN"])
    gh = Github(auth=auth)
    try:
        user = gh.get_user()
        print(f"\n  Conectado como: {user.login}")
    except GithubException as e:
        raise SystemExit(f"[ERROR] No se pudo conectar a GitHub: {e}")

    # Ejecutar pasos en orden
    repo = create_repository(gh)
    init_and_push(repo)
    setup_rulesets(repo)

    # Resumen final
    print("\n" + "=" * 60)
    print("  CONFIGURACION COMPLETADA")
    print("=" * 60)
    print(f"\n  Repositorio : {repo.html_url}")
    print(f"  Ramas       : main, dev")
    print(f"\n  Proximo paso: abrir un PR de dev a main para probar el pipeline de CI.\n")


if __name__ == "__main__":
    main()
