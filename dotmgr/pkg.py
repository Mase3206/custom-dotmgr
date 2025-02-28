#!/usr/bin/env python3.12

from __future__ import annotations

import subprocess
from abc import (
	ABC,  # abstract base class helper
	abstractmethod
)
from typing import Type, TypeVar, Dict

from dotmgr import outputs as out

if __name__ == '__main__':
	raise RuntimeError("This file should not be run directly.")


class UnknownSystemError(Exception):
	pass


def _command_exists(command: str) -> bool:
	return subprocess.run(
		f'command -v {command}', 
		shell=True, 
		stdout=subprocess.DEVNULL, 
		stderr=subprocess.DEVNULL
	).returncode == 0


T = TypeVar('T', bound='PackageManager')

class PackageManager(ABC):
	# keep track of all instances of subclasses of PackageManager
	_instances: Dict[Type[PackageManager], PackageManager] = {}

	prog: str
	'''The package manager's command-line program.'''
	install_sc: str
	'''The subcommand used for installing, ex: `install` or `add`.'''
	pkglist_update_sc: str
	'''Subcommand used for updating package list (not the packages).'''
	pkg_upgrade_sc: str
	'''Subcommand used for upgrading packages (not the list).'''

	def __new__(cls: Type[T], *args, **kwargs) -> T:
		if cls not in cls._instances:
			instance = super(PackageManager, cls).__new__(cls)
			cls._instances[cls] = instance
		return cls._instances[cls]  # type: ignore

	@abstractmethod
	def install(self, package: str):
		return self._run_command([self.prog, self.install_sc, '-y', package])

	def _run_command(self, command: list[str]):
		# run the command
		sp = subprocess.run(
			[*command],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			encoding='utf-8',
		)
		# if the command failed, print the stderr and raise an exception
		try:
			sp.check_returncode()
		except subprocess.CalledProcessError as e:
			# print(sp.stderr)
			raise e
		
		# otherwise, return the process.
		return sp

	@staticmethod
	def detect():  # returns instance of subtype
		'''
		Detects the system's package manager and returns its class, which is a subclass of PackageManager.

		Returns
		-------
			The subclass of `PackageManager` for your system's package manager.
		'''
		pairs = (
			('apt-get', AptGet),
			('dnf', Dnf),
			('brew', Brew),
		)
		for p in pairs:
			if _command_exists(p[0]):
				return p[1]()
		
		# if no match is found
		raise UnknownSystemError('Unknown system. Package manager could not be determined.')
	
	def __str__(self) -> str:
		return self.prog

class Dnf(PackageManager):
	prog = 'dnf'
	install_sc = 'install'
	pkglist_update_sc = 'refresh'
	pkg_upgrade_sc = 'update'

	def install(self, package: str):
		return super().install(package)

class AptGet(PackageManager):
	prog = 'apt-get'
	install_sc = 'install'
	pkglist_update_sc = 'update'
	pkg_upgrade_sc = 'upgrade'

	def install(self, package: str):
		# manually update package lists
		self._run_command([self.prog, self.pkglist_update_sc])
		return super().install(package)

class Brew(PackageManager):
	prog = 'brew'
	install_sc = 'install'
	pkglist_update_sc = 'update'
	pkg_upgrade_sc = 'upgrade'

	def install(self, package: str):
		return super().install(package)


PKGMGR = PackageManager.detect()
