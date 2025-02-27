#!/usr/bin/env python3.12

'''
Dotfile handling.
'''


from pathlib import Path
from dotmgr import HOME, PREFIX
from dotmgr import outputs as out
import shutil


class IsDirectoryError(FileExistsError):
	pass

class FileTypeError(Exception):
	pass

class ExistingForeignSymlinkError(FileExistsError):
	pass



class Dotfile:
	def __init__(self, relative_path: Path):
		'''
		Argument
		--------
			dotfiles_repo (Path) : Path to the dotfiles Git repo
			relative_path (Path) : Relative path to the source file from the dotfiles Git repo. This will also be the relative destination path of the symlink.
		'''
		self._prefix = HOME / PREFIX
		self._relative_path = relative_path
		# self.repo_src = dotfiles_repo / relative_path
		self.real_file = self._prefix / relative_path
		assert self.real_file.exists(), f'{self.real_file} must exist first!'
		self.link_dest = HOME / relative_path

	def rm_from_home(self, force = False):
		'''
		Remove the existing file or symlink from the user's home folder. Regular files are backed up instead of deleted.

		Attempting to remove a directory will throw an `IsDirectoryError`. To remove it anyway, call with force=True.

		Arguments
		---------
			force (bool) : Forcefully remove the targeted file (or directory, which is usually blocked). Defaults to `False`.
		'''
		# path to existing (or symlinked) dotfiles in ~/

		if self.link_dest.is_file(follow_symlinks = False):
			out.step(f'Backing up regular file {str(self.link_dest)}')

			# create backup of existing file 
			to = Path(*self.link_dest.parts[:-1]) / f'{self.link_dest.name}.bak'
			shutil.move(self.link_dest, to)

		elif self.link_dest.is_symlink():
			out.step(f'Removing symlink {str(self.link_dest)}')
			self.link_dest.unlink()  # removes the link

		elif self.link_dest.is_dir():
			if force:
				out.warn(f'Path {str(self.link_dest)} is a directory, but force=True. Removing {self.link_dest}')
				shutil.rmtree(self.link_dest)
			else:
				raise IsDirectoryError(f'Path {str(self.link_dest)} is a directory, refusing to remove.')

		elif not self.link_dest.exists:
			# raise FileNotFoundError(f'File {str(self.link_dest)} does not exist.')
			out.step(f'File {str(self.link_dest)} does not exist in ~/, which is okay! Skipping...')

		else:
			FileTypeError(f'Path {str(self.link_dest)} has an unknown type')

	def link(self, relink = False, remove_foreign_links = False):
		if self.link_dest.exists:
			# linked correctly
			if self.link_dest.readlink == self.real_file:
				if relink:
					out.step(f'Relinking {self.link_dest} to {self.real_file}')
				else:
					out.step(f'{self.link_dest} is already linked to {self.real_file}, skipping...')
			# linked incorrectly
			elif self.link_dest.is_symlink():
				# force
				if remove_foreign_links:
					out.step(f'{self.link_dest} is linked to {self.link_dest.readlink}, but it should be linked to {self.real_file}. Removing anyways, as remove_foreign_links is set to True.')
					self.rm_from_home()
				# except
				else:
					raise ExistingForeignSymlinkError(f'{self.link_dest} is already linked to foreign {self.link_dest.readlink}, but it should be linked to {self.real_file}. Not removing!')
			# except if dest is file or dir
			else:
				raise FileExistsError(f'Not removing existing file {self.link_dest} automatically.')
			
		# except if src is symlink
		elif self.real_file.is_symlink():
			raise FileTypeError(f'{self.real_file} is a symlink. Symlinking to another symlink is not supported by this program.')
		
		# allow if src is file or dir
		else:
			# warn linking dirs
			if self.real_file.is_dir():
				out.warn(f'Source {self.real_file} is a directory. This may lead to weird behavior. Beware!')
			
			out.step(f'Creating symlink from {self.real_file} to {self.link_dest}')
			self.link_dest.symlink_to(self.link_dest)  # make the link

		assert self.link_dest.readlink == self.real_file, f'{self.link_dest} should link to {self.real_file}, but it instead links to {self.link_dest.readlink}!'


	def __str__(self) -> str:
		return f'Symlink {self.link_dest} to {self.real_file}'
	
	def __repr__(self) -> str:
		return f'Dotfile(real_file=Path({str(self.real_file)}), link_dest=Path({str(self.link_dest)}))'
	
	def __eq__(self, other: object) -> bool:
		if isinstance(other, Dotfile):
			return self._relative_path == other._relative_path
		elif isinstance(other, str):
			return self._relative_path == other
		else:
			raise TypeError('Dotfiles can only be compared to other Dotfiles or relative string paths.')
