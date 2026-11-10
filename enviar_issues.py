#!/usr/bin/env python3
"""Previsualiza o publica mensaje.txt en los repositorios de repositorios.txt."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent


def gh(*args):
    result = subprocess.run(['gh', *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enviar', action='store_true', help='Publicar las issues en GitHub')
    parser.add_argument('--repos', type=Path, default=BASE / 'repositorios.txt')
    parser.add_argument('--mensaje', type=Path, default=BASE / 'mensaje.txt')
    parser.add_argument('--titulo', default='Questions about originality criteria — Meta AI Developer Hackathon 2026')
    args = parser.parse_args()
    body = args.mensaje.read_text(encoding='utf-8')
    if not body.strip() or not args.titulo.strip():
        parser.error('El mensaje y el título no pueden estar vacíos.')
    repos = []
    for line in args.repos.read_text(encoding='utf-8').splitlines():
        repo = line.strip()
        if not repo or repo.startswith('#'):
            continue
        repo = repo.removeprefix('https://github.com/').rstrip('/')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            parser.error(f'Repositorio inválido: {repo}')
        if repo.lower() not in [r.lower() for r in repos]:
            repos.append(repo)
    if not repos:
        parser.error('La lista de repositorios está vacía.')
    print(f'Título: {args.titulo}\n\n{body}\nDestinatarios ({len(repos)}):')
    print('\n'.join(repos))
    if not args.enviar:
        print('\nVista previa. Para publicar, añade --enviar.')
        return 0
    if not shutil.which('gh'):
        parser.error('Instala GitHub CLI (gh) e inicia sesión con gh auth login.')
    gh('auth', 'status', '--hostname', 'github.com')
    # Registro inmediato para revisar resultados y evitar repetir envíos exitosos.
    log_path = BASE / 'issues_enviadas.jsonl'
    sent = set()
    if log_path.exists():
        for line in log_path.read_text(encoding='utf-8').splitlines():
            record = json.loads(line)
            sent.add((record['repo'].lower(), record['titulo']))
    for repo in repos:
        if (repo.lower(), args.titulo) in sent:
            print(f'Omitido (ya registrado): {repo}')
            continue
        # Paginar todas las issues, incluidas las cerradas, sin depender del índice de búsqueda.
        try:
            pages = json.loads(gh('api', '--hostname', 'github.com', '--paginate', '--slurp',
                                 f'repos/{repo}/issues?state=all&per_page=100'))
        except RuntimeError as exc:
            if 'HTTP 404' in str(exc) or 'HTTP 410' in str(exc):
                print(f'Omitido (repositorio no accesible o Issues desactivadas): {repo}', flush=True)
                continue
            raise
        existing = next((issue for page in pages for issue in page
                         if 'pull_request' not in issue and issue['title'] == args.titulo), None)
        if existing:
            print(f'Omitido (título existente): {existing["html_url"]}')
            continue
        url = gh('issue', 'create', '--repo', f'https://github.com/{repo}',
                 '--title', args.titulo, '--body', body)
        with log_path.open('a', encoding='utf-8') as log:
            log.write(json.dumps({'repo': repo, 'titulo': args.titulo, 'url': url}) + '\n')
        print(f'Creada: {url}', flush=True)
        time.sleep(3)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'Envío detenido: {exc}\nRevisa el error antes de volver a ejecutar.', file=sys.stderr)
        sys.exit(1)
