"""
Additional code required to install programs that use or tend to some dotfiles, like Zsh.
"""

from dotmgr.pkg import PackageManager
from dotmgr.mods.core import ModManager

PKGMGR = PackageManager.detect()
MOD_MANAGER = ModManager()
