"""Order dated reports and include experiment pages without report metadata."""
import json
import re
from pathlib import Path


def page_title(path):
    return next(line[2:].strip() for line in path.read_text().splitlines() if line.startswith('# '))


def nav_paths(items):
    for item in items:
        for value in item.values():
            if isinstance(value, str):
                yield value
            else:
                yield from nav_paths(value)


def on_config(config):
    root = Path(config['docs_dir']) / 'experiments'
    reports = [(p.parent.name, json.loads(p.read_text())) for p in root.glob('*/report.json')]
    reports.sort(key=lambda entry: (entry[1]['date'], entry[0]), reverse=True)
    for section in config['nav']:
        if 'Experiments' in section:
            children = [{'Model runs': 'experiments/index.md'}]
            for stage, label in [('nowcast', 'Nowcasting'), ('forecast', 'Forecasting')]:
                pages = []
                for name, meta in reports:
                    if meta['stage'] != stage:
                        continue
                    title = f'{meta["date"]} · {meta["title"]}'
                    pages.append({title: f'experiments/{name}/index.md'})
                if pages:
                    children.append({label: pages})
            archived = [(p.parent.name, json.loads(p.read_text())) for p in (root / 'archive').glob('*/report.json')]
            archived.sort(key=lambda entry: (entry[1]['date'], entry[0]), reverse=True)
            if archived:
                children.append({'Archive': [{'Overview': 'experiments/archive/index.md'},
                    *[{f'{meta["date"]} · {meta["title"]}': f'experiments/archive/{name}/index.md'}
                      for name, meta in archived]]})
            # Handwritten reports and supporting notes do not all have report.json.
            # Group those pages by study instead of leaving them outside the menu.
            known = set(nav_paths(children))
            groups = {}
            for path in sorted(root.rglob('*.md')):
                relative = path.relative_to(root)
                if f'experiments/{relative.as_posix()}' in known:
                    continue
                groups.setdefault(relative.parts[0], []).append(path)
            additional = []
            for name, paths in sorted(groups.items(), key=lambda item: (
                    re.search(r'\d{8}', item[0]).group() if re.search(r'\d{8}', item[0]) else '',
                    item[0]), reverse=True):
                main = root / name / 'index.md'
                if not main.exists():
                    main = next((path for path in paths if path.name == 'protocol.md'), paths[0])
                ordered = sorted(paths, key=lambda path: (path != main, path.as_posix()))
                entries = [{page_title(path): f'experiments/{path.relative_to(root).as_posix()}'}
                           for path in ordered]
                additional.append(entries[0] if len(entries) == 1 else {page_title(main): entries})
            if additional:
                children.append({'Additional reports and notes': additional})
            section['Experiments'] = children
    return config
