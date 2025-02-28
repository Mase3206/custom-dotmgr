#!/usr/bin/env python3.12

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.request import urlretrieve

from dotmgr import outputs as out
from dotmgr.mods.core import Mod
from dotmgr.pkg import PKGMGR

class Zsh(Mod):
	required_file_names = ['.zshrc']
	alias = 'zsh'

	@classmethod
	def detect(cls) -> bool:
		if subprocess.run('zsh -c exit 0', shell=True).returncode == 0:
			out.good("Zsh install status", "already installed!")
			return True
		else:
			out.bad("Zsh install status", "NOT installed")
			return False
				

	def pre_install(self):
		return

	def install(self):
		super().install()

		if self.detect():
			print('Skipping Zsh installation.')
		else:
			out.subheader(f'Installing Zsh with {PKGMGR}')

			# PKGMGR.install('zsh')
		

	def post_install(self):
		for f in self.files:
			out.step(f'Linking Zsh files: {f}')
			# f.rm_from_home()
			# f.link()


class OhMyZsh(Mod):
	required_file_names = ['.oh-my-zsh']
	depends = [Zsh]
	alias = 'omz'


	def detect(self):
		if (Path('~/.oh-my-zsh')
			.resolve()
			.is_dir(follow_symlinks=False)
	  	):
			out.good('OMZ install status', 'already installed!')
			return True
		else:
			out.bad('OMZ install status', 'NOT installed.')
			return False
		

	def pre_install(self):
		return
		
	
	def install(self):
		super().install()

		if self.detect():
			print('Skipping Oh My Zsh installation.')
		else:
			out.subheader('Installing Oh My Zsh')

			USER = os.environ['USER']
			# temp_folder = Path(tempfile.mkdtemp())

			out.step('Downloading install script')
			# installer_path = Path(urlretrieve('https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh', temp_folder / 'install.sh')[0])

			out.step('Installing OMZ')
			# existing_environ = dict(os.environ.items())
			# subprocess.run(
			# 	['sh', installer_path, '--unattended', '--skip-chsh'],
			# 	env = {
			# 		'CHSH': 'yes',
			# 		'RUNZSH': 'no',
			# 		'KEEP_ZSHRC': 'yes',
			# 		**existing_environ
			# 	},
			# 	stdout = subprocess.DEVNULL,
			# 	stderr = subprocess.DEVNULL,
			# )

			out.step(f"Changing {USER}'s shell to /usr/bin/zsh")
			# subprocess.run(
			# 	['chsh', USER, '-s', '/usr/bin/zsh'],
			# 	stdout = subprocess.DEVNULL,
			# )

			out.step(f'Cleaning up')
			# shutil.rmtree(temp_folder)

			for f in self.files:
				out.step(f'Linking OMZ files: {f}')
				# f.rm_from_home(force=True)  # this shouldn't actually do anything, but do it just in case
				# f.link()

		
	def post_install(self):
		return


def _tc():
	from dotmgr.mods import MOD_MANAGER
	MOD_MANAGER.activate('zsh')

if __name__ == '__main__':
	_tc()
