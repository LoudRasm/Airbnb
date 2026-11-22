"""Sinh requirements.txt chỉ gồm thư viện bên thứ ba mà dự án THỰC SỰ import, ghim == theo venv đang chạy.

Cách dùng (chạy trong venv đã chạy được pipeline, từ thư mục gốc repo):
    python scripts/gen_requirements.py                       # chỉ thư viện import trực tiếp
    python scripts/gen_requirements.py --with-deps           # thêm cả thư viện phụ thuộc, ghim đủ để tái lập
    python scripts/gen_requirements.py --paths src scripts run_pipeline.py --out requirements.txt
Mặc định quét: src, scripts, tests, run_pipeline.py (không quét notebooks; thêm vào --paths nếu cần).
"""
import argparse
import ast
import re
import sys
from importlib import metadata
from pathlib import Path


def imported_modules(paths):
    found = {}
    for base in paths:
        base = Path(base)
        for file in ([base] if base.is_file() else sorted(base.rglob('*.py'))):
            if any(part in {'.venv', 'venv', '__pycache__', 'site-packages'} for part in file.parts):
                continue
            try:
                tree = ast.parse(file.read_text(encoding='utf-8'))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module]
                else:
                    continue
                for name in names:
                    found.setdefault(name.split('.')[0], set()).add(str(file))
    return found


def local_packages(paths):
    """Tên package/module nằm trong chính dự án (vd airbnb) để không nhầm là thư viện ngoài."""
    names = set()
    for base in paths:
        base = Path(base)
        if base.is_dir():
            names |= {p.name for p in base.iterdir() if p.is_dir() and (p / '__init__.py').exists()}
            names |= {p.stem for p in base.glob('*.py')}
        else:
            names.add(base.stem)
    return names


def dist_name(distribution):
    return re.sub(r'[-_.]+', '-', distribution).lower()


def requirements_of(dist):
    out = set()
    for line in metadata.requires(dist) or []:
        if 'extra ==' in line.replace('"', "'").replace("'", ''):
            continue                                   # bỏ phụ thuộc tùy chọn
        out.add(dist_name(re.split(r'[ ;<>=!~(\[]', line.strip(), maxsplit=1)[0]))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--paths', nargs='+', default=['src', 'scripts', 'tests', 'run_pipeline.py'])
    parser.add_argument('--out', default='requirements.txt')
    parser.add_argument('--with-deps', action='store_true', help='ghim thêm các thư viện phụ thuộc (transitive)')
    args = parser.parse_args()

    paths = [p for p in args.paths if Path(p).exists()]
    modules = imported_modules(paths)
    local = local_packages(paths)
    mapping = metadata.packages_distributions()        # tên module -> [tên distribution]
    direct, unresolved = {}, []
    for module, files in sorted(modules.items()):
        if module in sys.stdlib_module_names or module in local or module == '__future__':
            continue
        dists = mapping.get(module)
        if not dists:
            unresolved.append((module, sorted(files)[0]))
            continue
        direct[dist_name(dists[0])] = module

    wanted = set(direct)
    if args.with_deps:
        queue = list(wanted)
        while queue:
            for dep in requirements_of(queue.pop()):
                try:
                    metadata.version(dep)
                except metadata.PackageNotFoundError:
                    continue
                if dep not in wanted:
                    wanted.add(dep)
                    queue.append(dep)

    lines = [f'{name}=={metadata.version(name)}' for name in sorted(wanted)]
    header = ['# Sinh bằng scripts/gen_requirements.py từ venv đã chạy được pipeline.',
              f'# Python {sys.version.split()[0]}; {"gồm cả thư viện phụ thuộc" if args.with_deps else "chỉ thư viện import trực tiếp"}.']
    Path(args.out).write_text('\n'.join(header + lines) + '\n', encoding='utf-8')
    print(f'Đã ghi {args.out}: {len(lines)} thư viện ({len(direct)} import trực tiếp)')
    for name in sorted(direct):
        print(f'  {name}=={metadata.version(name)}   <- import {direct[name]}')
    for module, where in unresolved:
        print(f'  CẢNH BÁO: không tìm thấy thư viện cài đặt cho "import {module}" (trong {where}); cài hoặc bỏ import này.', file=sys.stderr)


if __name__ == '__main__':
    main()
