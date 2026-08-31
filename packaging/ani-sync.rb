class AniSync < Formula
  desc "Stream anime from terminal with 64x turbo speed & multi-platform tracking"
  homepage "https://github.com/idrisharis12/ani-sync"
  url "https://github.com/idrisharis12/ani-sync/archive/refs/tags/v2.9.0.tar.gz"
  sha256 "SKIP"
  license "MIT"

  depends_on "python@3.12"
  depends_on "fzf"
  depends_on "mpv"
  depends_on "yt-dlp"
  depends_on "curl"

  def install
    bin.install "ani_sync.py" => "ani-sync"
    doc.install "README.md", "CHEATSHEET.md"
  end

  test do
    system "#{bin}/ani-sync", "--help"
  end
end
