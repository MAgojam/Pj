"""Select a precompiled native backend for a disposable JMO build checkout.

The unfinished Rust source project is local-only and is not needed here.
Foreign platform directories are moved aside, never packaged or deleted.
"""
import argparse
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('platform', choices=['win_amd64', 'linux_x86_64', 'macosx_x86_64', 'macosx_arm64'])
args = parser.parse_args()
root = args.root.resolve(strict=True)
package = root / 'inst' / 'python' / 'pj_stats_rust'
selected = package / args.platform
filename = 'pj_stats_rust.pyd' if args.platform == 'win_amd64' else 'pj_stats_rust.abi3.so'
if not (selected / filename).is_file():
    parser.error('Missing precompiled native library: ' + str(selected / filename)
                 + '. Build and validate this platform separately; Rust source is not published in Pj.')
if package.is_symlink() or selected.is_symlink() or not selected.resolve().is_relative_to(root):
    parser.error('Unexpected native library path.')
for tag in ['win_amd64', 'linux_x86_64', 'macosx_x86_64', 'macosx_arm64']:
    source = package / tag
    if tag != args.platform and source.exists():
        destination = root / 'build-native-foreign' / tag
        if source.is_symlink() or not source.resolve().is_relative_to(root):
            parser.error('Unexpected foreign native path.')
        if destination.exists() or not destination.resolve().is_relative_to(root):
            parser.error('Use a fresh disposable checkout; foreign-binary backup already exists.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
catalog = root / 'inst' / 'extdata' / 'mzPj_native_libraries.json'
value = json.loads(catalog.read_text(encoding='utf-8'))
value['libraries'][0]['supported_platforms'] = [args.platform]
catalog.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
print('Precompiled native backend selected:', args.platform)
