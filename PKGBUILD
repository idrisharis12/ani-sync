# Maintainer: Idris Haris <https://github.com/idrisharis12>
pkgname=ani-sync
pkgver=2.2.0
pkgrel=1
pkgdesc="Stream anime from terminal with 64x turbo speed & automatic MyAnimeList tracking"
arch=('any')
url="https://github.com/idrisharis12/ani-sync"
license=('MIT')
depends=('python' 'python-requests' 'python-tqdm' 'mpv' 'yt-dlp' 'curl' 'fzf')
makedepends=('git' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz::https://github.com/idrisharis12/ani-sync/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver"
    install -Dm755 ani_sync.py "$pkgdir/usr/share/$pkgname/ani_sync.py"
    mkdir -p "$pkgdir/usr/bin"
    ln -s "/usr/share/$pkgname/ani_sync.py" "$pkgdir/usr/bin/ani-sync"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 CHEATSHEET.md "$pkgdir/usr/share/doc/$pkgname/CHEATSHEET.md"
    install -Dm644 CREDITS.md "$pkgdir/usr/share/doc/$pkgname/CREDITS.md"
}
