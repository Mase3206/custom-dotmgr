#!/usr/bin/env python3.12

import argparse
from pathlib import Path
from dotmgr import loader
from dotmgr.mods import Mod


def sync(args: argparse.Namespace):
	pass

def rm(args: argparse.Namespace):
	pass

def link(args: argparse.Namespace):
	if not args.conf_file and not args.path:
		parse_error('<path> is required when a config file is not given with `-c`.')
	
def install(args: argparse.Namespace):
	if not args.conf_file and not args.mod:
		parse_error('<mod> is required when a config file is not given with `-c`.')
	
	files = loader.load_files(args)
	mods = loader.load_mods(args)

	for m in mods:
		m(files = [f for f in files if f in m.required_file_names]).install()


def get_args(man_args = []):
	parser = argparse.ArgumentParser(prog='dotmgr')
	global parse_error
	parse_error = parser.error  # make a global alias to the parser.error function

	parser.add_argument('-c', help='Path to config.yml file', dest='conf_file', metavar='path', type=Path)


	sp_manager = parser.add_subparsers(required=True)

	sp_link = sp_manager.add_parser(
	    'link', 
	    description = 'Link file from given path (relative to user\'s home folder) from its expected real file.',
	)
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

	sp_install = sp_manager.add_parser(
		'install',
		description = 'Install mods.'
	)
	sp_install.add_argument('mod')

	sp_sync = sp_manager.add_parser(
	    'sync',
	    description = 'Sync (link or relink) all files from a config.'
	)
	sp_sync.set_defaults(func=sync)

	if man_args == []:
		args = parser.parse_args(man_args)
	else:
		args = parser.parse_args()

	return args




def main():
	args = get_args(man_args = ['install', 'omz'])
	args.func(args)


if __name__ == '__main__':
	main()
