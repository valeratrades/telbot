let
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/24.05.tar.gz") {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
      requests
			python-telegram-bot
    ]))
  ];
}
