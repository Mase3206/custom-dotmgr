"""
Additional code required to install programs that use or tend to some dotfiles, like Zsh.
"""

from dotmgr.mods.core import ModManager
from dotmgr.pkg import PackageManager

PKGMGR = PackageManager.detect()
MOD_MANAGER = ModManager()
