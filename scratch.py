def run_config_wizard():
    print(f"\n{C_CYAN}{C_BOLD}⚙️ Interactive Configuration Wizard{C_RESET}")
    print(f"{C_DIM}Set your default preferences so you don't have to type flags every time!{C_RESET}\n")

    # 1. Quality
    q_opts = ["1080p (Full HD)", "720p (HD - Fast/No Buffer)", "480p (SD)", "360p (Data Saver)"]
    q_vals = ["1080p", "720p", "480p", "360p"]
    q_idx = pick_option("📺 Select Default Quality:", q_opts, default_idx=1)
    _append_config("ANI_SYNC_DEFAULT_QUALITY", q_vals[q_idx])

    # 2. Audio Mode
    m_opts = ["Japanese SUB", "English DUB"]
    m_vals = ["sub", "dub"]
    m_idx = pick_option("🗣️ Select Default Audio:", m_opts, default_idx=0)
    _append_config("ANI_SYNC_DEFAULT_MODE", m_vals[m_idx])

    # 3. Provider
    p_opts = ["auto (Best Available)", "gogo", "hianime", "anidb"]
    p_vals = ["auto", "gogo", "hianime", "anidb"]
    p_idx = pick_option("📡 Select Default Provider:", p_opts, default_idx=0)
    _append_config("ANI_SYNC_DEFAULT_PROVIDER", p_vals[p_idx])

    # 4. Theme
    t_opts = ["catppuccin", "tokyonight", "dracula", "nord", "gruvbox", "monokai", "default"]
    t_idx = pick_option("🎨 Select FZF Theme:", t_opts, default_idx=0)
    _append_config("ANI_SYNC_THEME", t_opts[t_idx])

    print(f"\n{C_GREEN}✅ Configuration saved successfully to {CONFIG_PATH}!{C_RESET}")
    print(f"Run {C_CYAN}ani-sync{C_RESET} to enjoy your new defaults.")
