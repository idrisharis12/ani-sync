class AniSync < Formula
  desc "Stream anime from terminal with 64x turbo speed & auto MyAnimeList sync"
  homepage "https://github.com/idrisharis12/ani-sync"
  url "https://github.com/idrisharis12/ani-sync/archive/refs/tags/v2.0.0.tar.gz"
  sha256 "SKIP"
  license "MIT"

  depends_on "python@3.12"
  depends_on "mpv"
  depends_on "yt-dlp"

  def install
    bin.install "ani_sync.py" => "ani-sync"
  end

  test do
    system "#{bin}/ani-sync", "--help"
  end
end
