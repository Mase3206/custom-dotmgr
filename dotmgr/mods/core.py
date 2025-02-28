#!/usr/bin/env python3.12

from __future__ import annotations

if __name__ == '__main__':
	raise RuntimeError("This file should not be run directly.")


from abc import (
	ABC,  # abstract base class helper
	abstractmethod
)
from argparse import Namespace
from typing import List, Type

import yaml

from dotmgr import outputs as out
from dotmgr.files import DOTFILE_MANAGER, Dotfile


class MissingRequiredDotfileError(FileNotFoundError):
	pass


class Mod(ABC):
	files: list[Dotfile]  # references to Dotfile instances
	required_file_names: list[str]
	depends: List[Type[Mod]] = []  # these should be classes, not instances!
	alias: str

	def __init__(self) -> None:
		super().__init__()
		try:
			self.files = [
				DOTFILE_MANAGER.get(df)
				for df in self.required_file_names
			]
		except FileNotFoundError:
			raise MissingRequiredDotfileError(f'Missing one or more of the required dotfiles for this mod: {self.required_file_names}')
		
	
	def install_dependencies(self): 
		for dep in self.depends:
			if not dep.detect():
				dep().install()


	@classmethod
	@abstractmethod
	def detect(cls) -> bool: ...

	@abstractmethod
	def install(self): 
		self.install_dependencies()
		# extended by subclasses

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

	registered: dict[str, Type[Mod]]
	'''Mods known to the manager.'''
	active: list[Type[Mod]]
	'''Mods used by the user's config.'''


	def __init__(self):
		self.registered = {}
		self.active = []
	
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(ModManager, cls).__new__(cls)
		return cls.instance

	def register(self, mod: Type[Mod]):
		'''
		Make the given Mod subclass known by the global ModManager.

		Arguments
		---------
			mod (Type[Mod]) : The class object *(not an instance!)* of a subclass of Mod.
		'''
		if issubclass(mod, Mod):
			if self.registered.get(mod.alias, None):
				out.warn('Mod already registered. Skipping...')
			else:
				self.registered[mod.alias] = mod
		else:
			raise TypeError('Mod to register must be of a subclass of Mod.')

	def activate(self, alias: str) -> Type[Mod]:
		'''
		Search for the Mod by the given alias and mark it as used in this user's config.

		Arguments
		---------
			alias (str) : The alias of the Mod to activate.
		'''
		if alias not in self.active:
			if (mod := self.registered.get(alias, None)):
				self.active.append(mod)
			else:
				raise UnknownModError(f'No registered mod found with alias.')
		else:
			out.warn('Mod already activated.')
			mod = self[alias]
		
		return mod
	
	def install(self, mod: str | Type[Mod]):
		'''
		Install the given Mod.

		Arguments
		---------
			mod (str | Type[Mod]) : The alias of a Mod subclass or Mod subclass type itself.
		'''

		if isinstance(mod, str):
			mod = self.get_activated(mod)
		elif not issubclass(mod, Mod):
			raise TypeError('Mod to install must either be an alias or a subclass of Mod.')
		
		modInstance = mod()
		modInstance.install()

	
	
	def get_registered(self, alias: str) -> Type[Mod]:
		return self.registered[alias]
	
	def get_activated(self, alias: str) -> Type[Mod]:
		for m in self:
			if alias == m.alias:
				return m
		# if no match was found
		raise UnknownModError(f'No activated mod found with alias {alias}')

	def __len__(self):
		return len(self.active)
	
	def __iter__(self):
		return iter(self.active)

MOD_MANAGER = ModManager()



def load_mods(args: Namespace):
	'''
	Loads and activates each mod listed in the user's config file into the global MOD_MANAGER. 
	'''
	if args.conf_file:
		with open(args.conf_file, 'r') as f:
			raw_mods = yaml.safe_load(f).get('mods', [])
	else:
		raw_mods = [args.mod]

	for m in raw_mods:
		MOD_MANAGER.activate(m)

