#!/usr/bin/env python3

import os
import pathlib
import platform
import zipfile
import urllib.request
import shutil
import hashlib
import argparse
import sys
from pathlib import Path

# ============================================================================
# 平台构建开关配置
# 只启用 Windows 和 Android 构建，其他平台已禁用
# ============================================================================
ENABLE_WINDOWS = True      # Windows 桌面版
ENABLE_ANDROID = True      # Android 版
ENABLE_LINUX = False       # Linux 版 (已禁用)
ENABLE_MACOS = False       # macOS 版 (已禁用)
ENABLE_IOS = False         # iOS 版 (已禁用)

# ============================================================================
# 基础配置
# ============================================================================
windows = platform.platform().startswith('Windows')
osx = platform.platform().startswith('Darwin') or platform.platform().startswith("macOS")
hbb_name = 'jingyue_control' + ('.exe' if windows else '')
exe_path = 'target/release/' + hbb_name
if windows:
    flutter_build_dir = 'build/windows/x64/runner/Release/'
elif osx:
    flutter_build_dir = 'build/macos/Build/Products/Release/'
else:
    flutter_build_dir = 'build/linux/x64/release/bundle/'
flutter_build_dir_2 = f'flutter/{flutter_build_dir}'
skip_cargo = False


def system2(cmd):
    exit_code = os.system(cmd)
    if exit_code != 0:
        sys.stderr.write(f"Error occurred when executing: `{cmd}`. Exiting.\n")
        sys.exit(-1)


def get_version():
    with open("Cargo.toml", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("version"):
                return line.replace("version", "").replace("=", "").replace('"', '').strip()
    return ''


def get_features(args):
    features = ['inline'] if not args.flutter else []
    if args.hwcodec:
        features.append('hwcodec')
    if args.vram:
        features.append('vram')
    if args.flutter:
        features.append('flutter')
    if args.unix_file_copy_paste:
        features.append('unix-file-copy-paste')
    print("features:", features)
    return features


def make_parser():
    parser = argparse.ArgumentParser(description='JingyueControl Build Script (Windows & Android only)')
    parser.add_argument(
        '-f',
        '--feature',
        dest='feature',
        metavar='N',
        type=str,
        nargs='+',
        default='',
        help='Integrate features, windows only.')
    parser.add_argument('--flutter', action='store_true',
                        help='Build flutter package', default=False)
    parser.add_argument('--hwcodec', action='store_true',
                        help='Enable feature hwcodec')
    parser.add_argument('--vram', action='store_true',
                        help='Enable feature vram, only available on windows now.')
    parser.add_argument('--portable', action='store_true',
                        help='Build windows portable')
    parser.add_argument('--android', action='store_true',
                        help='Build Android APK')
    parser.add_argument('--android-release', action='store_true',
                        help='Build Android release APK')
    parser.add_argument('--skip-cargo', action='store_true',
                        help='Skip cargo build process')
    if windows:
        parser.add_argument('--skip-portable-pack', action='store_true',
                            help='Skip packing, only flutter version + Windows supported')
    parser.add_argument("--package", type=str)
    return parser


def external_resources(flutter, args, res_dir):
    # 简化版本，暂不下载外部资源
    pass


def build_flutter_windows(version, features, skip_portable_pack):
    """构建 Windows Flutter 版本"""
    print("=" * 60)
    print("Building Windows Flutter version...")
    print("=" * 60)

    if not skip_cargo:
        system2(f'cargo build --features {features} --lib --release')
        if not os.path.exists("target/release/libjingyue_control.dll"):
            print("cargo build failed, please check rust source code.")
            exit(-1)

    # 构建虚拟显示器动态库
    os.chdir('libs/virtual_display/dylib')
    system2('cargo build --release')
    os.chdir('../../..')

    os.chdir('flutter')
    system2('flutter build windows --release')
    os.chdir('..')

    shutil.copy2('target/release/deps/dylib_virtual_display.dll', flutter_build_dir_2)

    if skip_portable_pack:
        print(f"Windows build completed: {flutter_build_dir_2}")
        return

    # 打包 portable 版本
    os.chdir('libs/portable')
    system2('pip3 install -r requirements.txt')
    system2(
        f'python3 ./generate.py -f ../../{flutter_build_dir_2} -o . -e ../../{flutter_build_dir_2}/jingyue_control.exe')
    os.chdir('../..')

    if os.path.exists('./jingyue_control_portable.exe'):
        os.replace('./target/release/jingyue_control-portable-packer.exe',
                   './jingyue_control_portable.exe')
    else:
        os.rename('./target/release/jingyue_control-portable-packer.exe',
                  './jingyue_control_portable.exe')

    print(f'Portable exe location: {os.path.abspath(os.curdir)}/jingyue_control_portable.exe')
    os.rename('./jingyue_control_portable.exe', f'./jingyue_control-{version}-install.exe')
    print(f'Final installer location: {os.path.abspath(os.curdir)}/jingyue_control-{version}-install.exe')


def build_android(version, features, is_release=False):
    """构建 Android APK"""
    print("=" * 60)
    print(f"Building Android {'release' if is_release else 'debug'} APK...")
    print("=" * 60)

    if not skip_cargo:
        system2(f'cargo build --features {features} --lib --release')

    os.chdir('flutter')

    if is_release:
        system2('flutter build apk --release')
        apk_path = 'build/app/outputs/flutter-apk/app-release.apk'
        output_name = f'jingyue_control-{version}-android.apk'
    else:
        system2('flutter build apk --debug')
        apk_path = 'build/app/outputs/flutter-apk/app-debug.apk'
        output_name = f'jingyue_control-{version}-android-debug.apk'

    os.chdir('..')

    if os.path.exists(f'flutter/{apk_path}'):
        shutil.copy2(f'flutter/{apk_path}', output_name)
        print(f'APK location: {os.path.abspath(os.curdir)}/{output_name}')
    else:
        print(f'Warning: APK not found at flutter/{apk_path}')


# ============================================================================
# 以下平台构建函数已禁用 (Linux, macOS, iOS)
# ============================================================================

def build_flutter_deb(version, features):
    """Linux DEB 构建 - 已禁用"""
    if not ENABLE_LINUX:
        print("Linux build is disabled. Set ENABLE_LINUX=True to enable.")
        return
    # Linux 构建代码已注释
    # ...

def build_flutter_dmg(version, features):
    """macOS DMG 构建 - 已禁用"""
    if not ENABLE_MACOS:
        print("macOS build is disabled. Set ENABLE_MACOS=True to enable.")
        return
    # macOS 构建代码已注释
    # ...

def build_flutter_arch_manjaro(version, features):
    """Arch Linux 构建 - 已禁用"""
    if not ENABLE_LINUX:
        print("Linux build is disabled.")
        return

def build_flutter_ios(version, features):
    """iOS 构建 - 已禁用"""
    if not ENABLE_IOS:
        print("iOS build is disabled. Set ENABLE_IOS=True to enable.")
        return
    # iOS 构建代码已注释
    # ...

# ============================================================================
# 主函数
# ============================================================================
def main():
    global skip_cargo
    parser = make_parser()
    args = parser.parse_args()

    # 显示当前启用的平台
    print("=" * 60)
    print("JingyueControl Build Script")
    print("=" * 60)
    print(f"Enabled platforms:")
    print(f"  - Windows: {ENABLE_WINDOWS}")
    print(f"  - Android: {ENABLE_ANDROID}")
    print(f"  - Linux: {ENABLE_LINUX}")
    print(f"  - macOS: {ENABLE_MACOS}")
    print(f"  - iOS: {ENABLE_IOS}")
    print("=" * 60)

    if os.path.exists(exe_path):
        os.unlink(exe_path)

    version = get_version()
    features = ','.join(get_features(args))
    flutter = args.flutter

    if args.skip_cargo:
        skip_cargo = True

    # Android 构建
    if args.android or args.android_release:
        if not ENABLE_ANDROID:
            print("Android build is disabled.")
            return
        build_android(version, features, is_release=args.android_release)
        return

    # Windows 构建
    if windows and ENABLE_WINDOWS:
        if flutter:
            build_flutter_windows(version, features, args.skip_portable_pack if hasattr(args, 'skip_portable_pack') else False)
            return

        # 非 Flutter 版本 (Sciter，已弃用)
        system2('cargo build --release --features ' + features)
        system2('mv target/release/jingyue_control.exe target/release/JingyueControl.exe')
        print(f"Build completed: target/release/JingyueControl.exe")
        return

    # 其他平台 (已禁用)
    if not windows:
        print("Non-Windows platform detected but other platforms are disabled.")
        print("To enable other platforms, modify the ENABLE_* flags in build.py")
        print("Currently only Windows and Android builds are supported.")


if __name__ == "__main__":
    main()