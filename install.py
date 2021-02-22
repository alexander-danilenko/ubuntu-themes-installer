#!/usr/bin/env python3

import apt, os, subprocess, yaml

build_dir = os.path.abspath('./build')

# Just prints colored strings.
class Logger:
    channel: str
    def __init__(self, channel: str):
        self.channel = channel
    def log(self, message): # Green.
        print(f'\033[92m[{self.channel}] {message}\033[0m')
    def info(self, message): # Blue.
        print(f'\033[94m[{self.channel}] {message}\033[0m')
    def warning(self, message): # Yellow.
        print(f'\033[93m[{self.channel}] {message}\033[0m')
    def error(self, message): # Red.
        print(f'\033[91m[{self.channel}] {message}\033[0m')

# Handles item from YML file.
class InstallableItem:
    logger: Logger
    name: str
    group: str
    repo: str # URL of git repo.
    install: str # Install command.
    build_path: str # Directory path repo will be cloned to.

    def __init__(self, group: str, name: str, item: dict):
        self.repo = item['repo']
        self.name = name
        self.group = group
        self.logger = Logger(f'build/{self.group}/{self.name}')
        self.build_path = f'{build_dir}/{self.group}/{self.name}'
        self.install = item['install'].replace('{build}', build_dir)
        # Make sure group directory is created.
        os.makedirs(f'{build_dir}/{self.group}', exist_ok=True)

    # Downloads item.
    def clone(self):
        # If current item not downloaded.
        if not os.path.exists(self.build_path):
            self.logger.log(f'📥 Downloading to: {self.build_path}')
            subprocess.run(f'git clone {self.repo} {self.build_path} --depth=1 --quiet', shell=True, capture_output=False)
        return self

    # Runs install commands in repo directory.
    def run_install(self):
        self.logger.info('🔧 ' + self.install)
        subprocess.run(f'{self.install}', shell=True, capture_output=False, cwd=self.build_path)
        return self

# Installs apt packages required for themes building and installation.
def install_apt_prerequisites(packages):
    apt_install = []
    for package in packages:
        if not apt.cache.Cache()[package].installed:
            apt_install.append(package)
    if len(apt_install):
        subprocess.run('sudo apt install ' + ' '.join(apt_install), shell=True)

# Parse YML file.
with open('themes.yml') as config:
    settings = yaml.load(config, Loader=yaml.FullLoader)
    install_apt_prerequisites(settings.get('apt_prerequisites'))
    themes = settings.get('themes')
    logger = Logger('installer')

    # Just ask for sudo for future use.
    subprocess.run('sudo echo ""', shell=True)

    logger.log("🎉 Let's get the party started!")
    for group in themes:
        for name in themes.get(group):
            InstallableItem(group, name, themes.get(group).get(name)).clone().run_install()
    logger.log('🥳 Themes installation complete! Enjoy your awesomeness!')
