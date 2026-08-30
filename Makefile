PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
SHAREDIR ?= $(PREFIX)/share/ani-sync

install:
	@echo "Installing ani-sync to $(BINDIR)..."
	@mkdir -p $(BINDIR) $(SHAREDIR)
	@cp ani_sync.py $(SHAREDIR)/ani_sync.py
	@chmod +x $(SHAREDIR)/ani_sync.py
	@printf '#!/usr/bin/env bash\nexec python3 $(SHAREDIR)/ani_sync.py "$$@"\n' > $(BINDIR)/ani-sync
	@chmod +x $(BINDIR)/ani-sync
	@echo "✓ Successfully installed ani-sync."

uninstall:
	@echo "Uninstalling ani-sync..."
	@rm -f $(BINDIR)/ani-sync
	@rm -rf $(SHAREDIR)
	@echo "✓ Successfully uninstalled ani-sync."
