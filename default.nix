{ lib
, python3Packages
, fetchFromGitHub
, makeWrapper
, mpv
, yt-dlp
, fzf
, curl
}:

python3Packages.buildPythonApplication rec {
  pname = "ani-sync";
  version = "2.1.0";
  format = "other";

  src = ./.;

  nativeBuildInputs = [ makeWrapper ];

  propagatedBuildInputs = with python3Packages; [
    requests
    tqdm
  ];

  installPhase = ''
    mkdir -p $out/bin $out/share/ani-sync
    cp ani_sync.py $out/share/ani-sync/
    makeWrapper ${python3Packages.python.interpreter} $out/bin/ani-sync \
      --add-flags "$out/share/ani-sync/ani_sync.py" \
      --prefix PATH : ${lib.makeBinPath [ mpv yt-dlp fzf curl ]} \
      --prefix PYTHONPATH : "$PYTHONPATH"
  '';

  meta = with lib; {
    description = "Stream anime in terminal with 64x turbo speed & automatic MyAnimeList/AniList/Kitsu tracking";
    homepage = "https://github.com/idrisharis12/ani-sync";
    license = licenses.mit;
    maintainers = [ ];
    mainProgram = "ani-sync";
  };
}
