{ pkgs ? import <nixpkgs> {} }:

pkgs.python3Packages.buildPythonApplication rec {
  pname = "ani-sync";
  version = "2.11.26";

  src = ./.;

  format = "pyproject";

  nativeBuildInputs = with pkgs.python3Packages; [
    setuptools
  ];

  propagatedBuildInputs = with pkgs.python3Packages; [
    requests
    tqdm
  ];

  doCheck = false;

  meta = with pkgs.lib; {
    description = "Stream anime from terminal with 64x turbo speed & automatic MyAnimeList tracking";
    homepage = "https://github.com/idrisharis12/ani-sync";
    license = licenses.mit;
    maintainers = [];
  };
}
