#!/usr/bin/env python3
"""Install or restore using Android SDK adb; no device address is stored."""
import argparse
from pathlib import Path
import shutil
import subprocess

PKG = 'com.jack.insigniahome'
SERVICE = PKG + '/com.gathin.tvhome.HomeKeyService'
ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['install', 'restore'])
    p.add_argument('--serial', required=True, help='adb serial (connect with adb connect TV_IP:5555 first)')
    args = p.parse_args()
    adb = shutil.which('adb')
    if not adb:
        p.error('Android SDK platform-tools/adb must be on PATH')
    prefix = [adb, '-s', args.serial]

    def run(*parts):
        return subprocess.check_output(prefix + list(parts), text=True).strip()

    def shell(*parts):
        return run('shell', *parts)

    if args.action == 'install':
        # This integration is intentionally specific; no universal Fire TV claim.
        model = shell('getprop', 'ro.product.model')
        sdk = shell('getprop', 'ro.build.version.sdk')
        if model != 'AFTHY7ABBA' or sdk != '30':
            p.error(f'Only AFTHY7ABBA / Android SDK 30 has been tested; found {model} / {sdk}')
        apk = ROOT / 'launcher/app/build/outputs/apk/release/app-release.apk'
        if not apk.is_file():
            p.error('Build first with ./build.command')
        result = run('install', '-r', str(apk))
        print(result)
        if 'Success' not in result:
            raise SystemExit('Install failed; Home settings were not changed')

    current = shell('settings', 'get', 'secure', 'enabled_accessibility_services')
    services = [s for s in current.split(':') if s and s != 'null']
    if args.action == 'install':
        if SERVICE not in services:
            services.append(SERVICE)
        value = ':'.join(services)
        # adb shell joins arguments: quote settings values for the remote shell.
        import shlex
        shell('settings', 'put', 'secure', 'enabled_accessibility_services', shlex.quote(value))
        shell('settings', 'put', 'secure', 'accessibility_enabled', '1')
        print(shell('am', 'start', '-W', '-n', PKG + '/com.gathin.tvhome.MainActivity'))
    else:
        services = [s for s in services if s != SERVICE]
        if services:
            import shlex
            shell('settings', 'put', 'secure', 'enabled_accessibility_services', shlex.quote(':'.join(services)))
        else:
            shell('settings', 'delete', 'secure', 'enabled_accessibility_services')
            shell('settings', 'put', 'secure', 'accessibility_enabled', '0')
        shell('am', 'force-stop', PKG)
        shell('input', 'keyevent', 'HOME')
        print('Amazon Home restored; no apps or packages were removed.')


if __name__ == '__main__':
    main()
