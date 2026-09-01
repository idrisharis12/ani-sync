class AniSync < Formula
  desc "Stream anime from terminal with 64x turbo speed & multi-platform tracking"
  homepage "https://github.com/idrisharis12/ani-sync"
  url "https://github.com/idrisharis12/ani-sync/archive/refs/tags/v2.11.11.tar.gz"
  sha256 "SKIP"
  license "MIT"

  depends_on "python@3.12"
  depends_on "fzf"
  depends_on "mpv"
  depends_on "yt-dlp"
  depends_on "curl"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/63/70/2bf7780ad2d390a8d301ad0b550f1581eadbd9a20f896afe06353c2a2913/requests-2.32.3.tar.gz"
    sha256 "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/a8/4b/29b4ef32e036bb34e4ab51796dd745cdba7ed47ad142a9f4a1eb8e0c744d/tqdm-4.67.1.tar.gz"
    sha256 "f8aef9c52c08c13a65f30ea34f4e5aac3fd1a34959b7f74571d160e6d14dbbe1"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/ani-sync", "--help"
  end
end
