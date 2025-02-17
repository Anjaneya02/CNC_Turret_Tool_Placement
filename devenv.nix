{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = with pkgs; [ git lazygit ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    package = pkgs.python312;
    poetry = {
      enable = true;
      activate.enable = true;
      install = {
        enable = true;
        quiet = true;
      };
    };
  };

  enterShell = ''
    devenv --version
  '';

  scripts.run.exec = ''
    poetry run python src/__main__.py
  '';

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
