# -*- coding: utf-8 -*-
"""
seed_data.py -- Carrega todos os XMLs de data/ no banco via HTTP (demo QA com mongomock).

Fluxo de demo QA (USE_MONGOMOCK=true):
    1. Suba a API:       python run.py
    2. Carregue os XMLs: python seed_data.py
    3. Explore os dados: http://localhost:8000/docs
    4. Para resetar:     Ctrl+C -> python run.py  (banco in-memory e limpo ao reiniciar)

Opcoes:
    python seed_data.py                          # Carrega data/*.xml (project e environment do XML/nome)
    python seed_data.py --project gdcr --env uat # Forca project/environment para todos os arquivos
    python seed_data.py --clean                  # Exibe instrucao de reset (banco in-memory: reinicie a API)
    python seed_data.py --dir legado             # Usa outra pasta ao inves de data/

Nota: Todo o seed e feito via HTTP. Nenhum componente da aplicacao e importado diretamente.
"""

import os
import sys
import glob
import argparse

import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DATA_DIR = "data"
DEFAULT_BASE_URL = "http://localhost:8000"


def get_api_key() -> str:
    """Resolve API key: CLI arg > .env > fallback."""
    return os.getenv("API_KEY", "dev-local-key")


def clean_database(base_url: str, headers: dict):
    """Instrui o usuario a reiniciar a API para limpar o banco in-memory.

    Com USE_MONGOMOCK=true, o banco vive na memoria do processo da API.
    A unica forma de limpa-lo e reiniciando a API (Ctrl+C -> python run.py).
    Importar create_app() aqui criaria uma segunda instancia isolada do
    mongomock -- diferente da usada pela API -- resultando em operacoes no
    banco errado.
    """
    print("\n[INFO] O banco in-memory (mongomock) e limpo ao reiniciar a API.")
    print("       Faca: Ctrl+C -> python run.py")
    sys.exit(0)


def extract_metadata_from_filename(filepath: str) -> dict:
    """Tenta extrair project/environment do nome do arquivo.

    Convencoes suportadas:
        data/1.xml                     -> project="default", env="uat"
        data/gdcr_uat_1.xml            -> project="gdcr", env="uat"
        data/gdcr/uat/1.xml            -> project="gdcr", env="uat"
        data/meu-projeto_rc_42.xml     -> project="meu-projeto", env="rc"
    """
    basename = os.path.splitext(os.path.basename(filepath))[0]
    parts = basename.split("_")

    # Se tiver subpastas: data/<project>/<env>/file.xml
    rel_path = os.path.relpath(filepath, DEFAULT_DATA_DIR)
    path_parts = rel_path.replace("\\", "/").split("/")
    if len(path_parts) >= 3:
        return {"project": path_parts[0], "environment": path_parts[1]}

    # Se o nome tiver formato project_env_number
    if len(parts) >= 3:
        env_candidate = parts[-2].lower()
        if env_candidate in ("uat", "rc", "unit", "dev", "staging", "prod"):
            return {"project": "_".join(parts[:-2]), "environment": env_candidate}

    # Se o nome tiver formato project_env
    if len(parts) == 2:
        env_candidate = parts[-1].lower()
        if env_candidate in ("uat", "rc", "unit", "dev", "staging", "prod"):
            return {"project": parts[0], "environment": env_candidate}

    # Fallback
    return {"project": "default", "environment": "uat"}


def upload_file(
    base_url: str,
    filepath: str,
    project: str,
    environment: str,
    headers: dict,
    source: str = "xml",
) -> dict:
    """Faz upload de um arquivo XML via endpoint /xml-execution/process-and-save."""
    with open(filepath, "rb") as f:
        files_dict = {"file": (os.path.basename(filepath), f, "application/xml")}
        params = {
            "project": project,
            "environment": environment,
            "source": source,
        }
        response = httpx.post(
            f"{base_url}/xml-execution/process-and-save",
            headers=headers,
            files=files_dict,
            params=params,
            timeout=30.0,
        )
    return {"status": response.status_code, "body": response.json()}


def main():
    parser = argparse.ArgumentParser(
        description="Seed: carrega XMLs de test results no banco via API"
    )
    parser.add_argument(
        "--dir", default=DEFAULT_DATA_DIR,
        help=f"Pasta com os XMLs (default: {DEFAULT_DATA_DIR})"
    )
    parser.add_argument(
        "--project", default=None,
        help="Forcar nome do projeto para todos os arquivos"
    )
    parser.add_argument(
        "--env", default=None,
        help="Forcar environment (uat/rc/unit) para todos os arquivos"
    )
    parser.add_argument(
        "--url", default=DEFAULT_BASE_URL,
        help=f"URL base da API (default: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Exibe instrucao de reset do banco in-memory (reinicie a API)"
    )
    parser.add_argument(
        "--source", default="xml",
        help="Fonte dos testes (default: xml)"
    )
    args = parser.parse_args()

    api_key = get_api_key()
    headers = {"X-API-Key": api_key}

    # --clean: instrui a reiniciar a API (banco in-memory e limpo ao reiniciar).
    # Verificado antes do health check: nao precisa da API rodando para exibir orientacao.
    if args.clean:
        clean_database(args.url, headers)

    # Verificar se a API esta rodando
    try:
        r = httpx.get(f"{args.url}/health/live", timeout=5.0)
        if r.status_code != 200:
            print(f"[ERRO] API nao esta respondendo em {args.url}")
            sys.exit(1)
    except httpx.ConnectError:
        print(f"[ERRO] Nao foi possivel conectar em {args.url}")
        print("       Certifique-se de que a API esta rodando: python run.py")
        sys.exit(1)

    print(f"[OK] API conectada em {args.url}")

    # Encontrar XMLs
    import re
    def natural_keys(text):
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

    xml_pattern = os.path.join(args.dir, "**", "*.xml")
    files = sorted(glob.glob(xml_pattern, recursive=True), key=natural_keys)

    if not files:
        print(f"\n[AVISO] Nenhum arquivo XML encontrado em {args.dir}/")
        print(f"        Coloque seus arquivos JUnit XML em {args.dir}/ e rode novamente")
        sys.exit(0)

    print(f"\n[INFO] Encontrados {len(files)} arquivo(s) XML em {args.dir}/")
    print("-" * 60)

    success = 0
    errors = 0

    for filepath in files:
        # Determinar project/environment
        if args.project and args.env:
            meta = {"project": args.project, "environment": args.env}
        else:
            meta = extract_metadata_from_filename(filepath)
            if args.project:
                meta["project"] = args.project
            if args.env:
                meta["environment"] = args.env

        rel_name = os.path.relpath(filepath, args.dir)
        print(
            f"  -> {rel_name}  "
            f"[project={meta['project']}, env={meta['environment']}]",
            end="  ",
        )

        try:
            result = upload_file(
                args.url, filepath,
                meta["project"], meta["environment"],
                headers, args.source,
            )
            if result["status"] in (200, 201):
                exec_id = result["body"].get("id", "?")
                print(f"[OK] id={exec_id}")
                success += 1
            else:
                msg = result["body"].get("detail", result["body"])
                print(f"[ERRO] {result['status']}: {msg}")
                errors += 1
        except Exception as e:
            print(f"[ERRO] {e}")
            errors += 1

    print("-" * 60)
    print(f"\n[RESULTADO] {success} sucesso, {errors} erro(s), {len(files)} total")

    if success > 0:
        print(f"\n[DOCS] Acesse o Swagger para ver os dados: {args.url}/docs")
        print(f"       GET /projects    -> listar projetos carregados")
        print(f"       GET /executions  -> ver execucoes")


if __name__ == "__main__":
    main()
