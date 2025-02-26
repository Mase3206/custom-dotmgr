#!/usr/bin/env python3.12

import argparse
from pathlib import Path
from dotmgr.files import Dotfile
import yaml



def from_conf(raw_conf: list[str | dict], parent = '') -> list[Dotfile]:
	files: list[Dotfile] = []

	for value in raw_conf:
		if type(value) == dict:
			fname = list(value.keys())[0]
			if type(value[fname]) == list:
				# handle multiple different files in a folder
				files += from_conf(
					value[fname],
					parent = f'{fname}/'
				)
			# elif type(value[fname]) == dict:  # TODO: eventual support for symlinking to multiple locations
			else:
				raise TypeError()
		elif type(value) == str:
			files += [Dotfile(Path(parent + value))]
		else:
			raise TypeError('File conf items must be either str paths or dicts.')

	return files



def link(args: argparse.Namespace):
	files: list[Dotfile]

	if args.conf_file:
		with open(args.conf_file, 'r') as f:
			files = from_conf(yaml.safe_load(f).get('files'))
	else:
		files = [Dotfile(args.path)]

	print(files)


def sync(args: argparse.Namespace):
	pass

def rm(args: argparse.Namespace):
	pass



def get_args():
	parser = argparse.ArgumentParser(prog='dotmgr')
	sp_manager = parser.add_subparsers(required=True)


	sp_link = sp_manager.add_parser(
	    'link', 
	    description = 'Link file from given path (relative to user\'s home folder) from its expected real file.',
	)
	sp_link.add_argument('-c', help='Path to config.yml file', dest='conf_file', metavar='path', type=Path)
	sp_link.add_argument('--force', help='Remove the destination if it\'s a symlink pointing to a foreign (incorrect) file', action=argparse._StoreTrueAction)
	sp_link.add_argument('-r', help='Allow re-linking of an existing destination symlink', action=argparse._StoreTrueAction)
	sp_link.add_argument('path', help='Relative path to the symlink.', type=Path, nargs='?')
	sp_link.set_defaults(func=link)

	sp_rm = sp_manager.add_parser(
	    'rm',
	    description = 'Remove existing dotfile from your home directory.'
	)
	sp_rm.add_argument('path', help='Relative path to the dotfile (or symlink) in your home directory', type=Path)
	sp_rm.set_defaults(func=rm)

	sp_sync = sp_manager.add_parser(
	    'sync',
	    description = 'Sync (link or relink) all files from a config.'
	)
	sp_sync.add_argument('config_path', help='Path to config.yml file', type=Path)
	sp_sync.set_defaults(func=sync)


	args = parser.parse_args()
	if not args.conf_file and not args.path:
		parser.error('<name> is required when a config file is not given with `-c`.')

	return args




def main():
	args = get_args()
	args.func(args)


if __name__ == '__main__':
	main()
