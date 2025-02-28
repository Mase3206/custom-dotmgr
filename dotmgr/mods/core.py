#!/usr/bin/env python3.12

from __future__ import annotations

if __name__ == '__main__':
	raise RuntimeError("This file should not be run directly.")


from abc import (
	ABC,  # abstract base class helper
	abstractmethod,
)
from typing import Type, List

from dotmgr import outputs as out
from dotmgr.files import Dotfile
from argparse import Namespace
import yaml



class Mod(ABC):
	files: list[Dotfile]  # references to Dotfile instances
	required_file_names: list[str]
	depends: List[Type[Mod]] = []  # these should be classes, not instances!
	alias: str

	def __init__(self) -> None:
		super().__init__()
		# if in_both(self.required_file_names, files):
		# 	self.files = files
		# else:
		# 	raise ValueError('Missing one or more required dotfiles for this mod.')

	def install_dependencies(self, args): 
		for dep in self.depends:
			if not dep.detect():
				dep().install()

	@abstractmethod
	@classmethod
	def detect(cls) -> bool: ...

	@abstractmethod
	def install(self): ...

	@abstractmethod
	def pre_install(self): ...

	@abstractmethod
	def post_install(self): ...




class UnknownModError(KeyError):
	pass

class ModManager:
	'''
	Manager for all Mods. Keeps track of which mods are registered (known) and activated (used), and allows for easy querying of registered and activated mods.
	'''

	registered: dict[str, Mod]
	'''Mods known to the manager.'''
	active: list[Mod]
	'''Mods used by the user's config.'''


	def __init__(self):
		self.registered = {}
		self.active = []

	def register(self, mod: Mod):
		if isinstance(mod, Mod):
			if self.registered.get(mod.alias, None):
				out.warn('Mod already registered. Skipping...')
			else:
				self.registered[mod.alias] = mod
		else:
			raise TypeError('Mod to register must be of a subclass of BaseMod')

	def activate(self, alias: str) -> Mod:
		if alias not in self.active:
			if (mod := self.registered.get(alias, None)):
				self.active.append(mod)
			else:
				raise UnknownModError(f'No registered mod found with alias.')
		else:
			out.warn('Mod already activated.')
			mod = self[alias]
		
		return mod
	
	
	def get_registered(self, alias: str) -> Mod:
		return self.registered[alias]
	
	def get_activated(self, alias: str) -> Mod:
		for m in self:
			if alias == m.alias:
				return m
		# if no match was found
		raise UnknownModError(f'No activated mod found with alias {alias}')

	def __len__(self):
		return len(self.active)
	
	def __iter__(self):
		return iter(self.active)



def load_mods(args: Namespace):
	mods = []

	if args.conf_file:
		with open(args.conf_file, 'r') as f:
			mods = yaml.safe_load(f).get('mods', [])
	else:
		mods = []

	return mods	

