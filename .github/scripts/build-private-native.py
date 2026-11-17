"""Build a native macOS backend from an explicitly authorised temporary encrypted input.

The private Rust project is never checked into Git or included in upload artifacts.
Only the native binary and its provenance report leave this temporary build folder.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

module = Path(sys.argv[1]).resolve(strict=True)
output = Path(sys.argv[2]).resolve()
asset_id = os.environ['PJ_NATIVE_SOURCE_ASSET']
plain_sha = os.environ['PJ_NATIVE_SOURCE_SHA256']
cipher_sha = os.environ['PJ_NATIVE_CIPHER_SHA256']
if not asset_id.isdigit() or any(len(value) != 64 or any(c not in '0123456789abcdef' for c in value)
                               for value in (plain_sha, cipher_sha)):
    raise SystemExit('Invalid temporary source asset or checksum.')
if not os.environ.get('PJ_PRIVATE_NATIVE_KEY_160'):
    raise SystemExit('The authorised temporary decryption secret is unavailable.')
arch = platform.machine()
if sys.platform != 'darwin' or arch not in ('arm64', 'x86_64'):
    raise SystemExit('This workflow needs a native macOS runner.')
tag = 'macosx_' + arch
with tempfile.TemporaryDirectory(prefix='pj-private-native-', dir=os.environ['RUNNER_TEMP']) as temporary:
    private = Path(temporary)
    cipher = private / 'source.enc'
    with cipher.open('wb') as stream:
        subprocess.run(['gh', 'api', 'repos/' + os.environ['GITHUB_REPOSITORY'] + '/releases/assets/' + asset_id,
                        '-H', 'Accept: application/octet-stream'], stdout=stream, check=True)
    if hashlib.sha256(cipher.read_bytes()).hexdigest() != cipher_sha:
        raise SystemExit('Encrypted source checksum mismatch.')
    archive = private / 'source.tar.gz'
    subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-iter', '200000', '-md', 'sha256',
                    '-pass', 'env:PJ_PRIVATE_NATIVE_KEY_160', '-in', str(cipher), '-out', str(archive)], check=True)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != plain_sha:
        raise SystemExit('Decrypted source checksum mismatch.')
    project = private / 'project'
    project.mkdir()
    with tarfile.open(archive, 'r:gz') as bundled:
        for member in bundled.getmembers():
            parts = Path(member.name).parts
            if (not parts or parts[0] != 'pj_stats_rust' or '..' in parts or Path(member.name).is_absolute()
                    or not (member.isfile() or member.isdir())):
                raise SystemExit('Unsupported private-source archive member.')
        bundled.extractall(project, filter='data')
    package = project / 'inst' / 'python' / 'pj_stats_rust'
    package.mkdir(parents=True)
    shutil.copy2(module / 'inst/python/pj_stats_rust/__init__.py', package / '__init__.py')
    extdata = project / 'inst' / 'extdata'
    extdata.mkdir(parents=True)
    shutil.copy2(module / 'inst/extdata/mzPj_native_libraries.json', extdata)
    shutil.copy2(module / 'inst/extdata/mzPj_icon_python.png', extdata)
    examples = project / 'pjscript'
    examples.mkdir()
    for filename in ('71_rust_stats_descriptives.py', '72_rust_batch_inference.py', '73_rust_repeated_measures.py'):
        shutil.copy2(module / 'pjscript' / filename, examples / filename)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    # The compiler/tests do not need either GitHub token or the decryption key.
    for name in ('GH_TOKEN', 'GITHUB_TOKEN', 'PJ_PRIVATE_NATIVE_KEY_160'):
        env.pop(name, None)
    # PyO3 extension symbols are supplied by the importing Python process on macOS.
    env['RUSTFLAGS'] = (env.get('RUSTFLAGS', '') + ' -Awarnings -C link-arg=-undefined -C link-arg=dynamic_lookup').strip()
    # Compiler diagnostics can quote private Rust source lines: keep them off public logs.
    result = subprocess.run([sys.executable, '-B', str(project / 'pj_stats_rust/build_native.py')],
                            env=env, capture_output=True, text=True)
    if result.returncode:
        safe_errors = [line for line in result.stderr.splitlines()
                       if line.startswith(('error:', 'error[', 'AssertionError:', 'ImportError:', 'ModuleNotFoundError:'))]
        for line in safe_errors:
            print(line, file=sys.stderr)
        raise SystemExit('Private native compilation/tests failed; no private source diagnostics published.')
    print('Native compilation and native/repeated-measures reference tests PASSED.')
    binary = package / tag / 'pj_stats_rust.abi3.so'
    subprocess.run(['lipo', str(binary), '-verify_arch', arch], check=True)
    destination = output / tag
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(binary, destination / binary.name)
    catalog = json.loads((extdata / 'mzPj_native_libraries.json').read_text(encoding='utf-8'))
    report = dict(version=catalog['libraries'][0]['version'], platform=tag,
                  sourceCommit=os.environ['GITHUB_SHA'], privateSourceSha256=plain_sha,
                  sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                  nativeTests='test_native.py and test_repeated.py PASSED',
                  python=sys.version, rust=subprocess.check_output(['rustc', '--version'], text=True).strip(),
                  privateSourceIncluded=False)
    (output / 'BUILD_NATIVE.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Native binary and numerical references PASSED; temporary private source removed:', tag)
