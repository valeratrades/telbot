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


{
  inputs = {
    nixpkgs.url = "https://github.com/NixOS/nixpkgs/archive/24.05.tar.gz";
    flake-utils.url = "github:numtide/flake-utils";
    v-utils.url = "github:valeratrades/.github";
  };

  outputs = { self, nixpkgs, flake-utils, v-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
      in
      {
        devShells.default = pkgs.mkShell {
					packages = [
						(pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
							requests
							python-telegram-bot
						]))
					];

          shellHook =
            ''
						cp -f ${(import v-utils.hooks.treefmt {inherit pkgs;})} ./.treefmt.toml

						cp -f ${(import v-utils.files.gitignore) { inherit pkgs; langs = ["py"];}} ./.gitignore
						'';
        };
      }
    );
}
