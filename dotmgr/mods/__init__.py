"""
Additional code required to install programs that use or tend to some dotfiles, like Zsh.
"""

from dotmgr.pkg import PackageManager

PKGMGR = PackageManager.detect()