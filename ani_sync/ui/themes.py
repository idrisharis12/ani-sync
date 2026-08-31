# -*- coding: utf-8 -*-
"""Terminal colors, ANSI escape sequences, and 24-bit TrueColor themes."""

THEMES = {
    "default": {
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "magenta": "\033[95m",
        "red": "\033[91m",
        "white": "\033[97m",
        "fzf_colors": "header:bold:cyan,info:yellow,prompt:bold:magenta,pointer:bold:cyan,marker:bold:green,border:cyan",
    },
    "tokyonight": {
        "blue": "\033[38;2;122;162;247m",
        "cyan": "\033[38;2;125;207;255m",
        "green": "\033[38;2;158;206;106m",
        "yellow": "\033[38;2;224;175;104m",
        "magenta": "\033[38;2;187;154;247m",
        "red": "\033[38;2;247;118;142m",
        "white": "\033[38;2;192;202;245m",
        "fzf_colors": "bg+:#283457,bg:#1a1b26,spinner:#ff007c,hl:#5883cf,fg:#c0caf5,header:#7aa2f7,info:#e0af68,pointer:#7dcfff,marker:#9ece6a,prompt:#bb9af7,hl+:#ff007c,border:#7aa2f7",
    },
    "catppuccin": {
        "blue": "\033[38;2;137;180;250m",
        "cyan": "\033[38;2;148;226;213m",
        "green": "\033[38;2;166;227;161m",
        "yellow": "\033[38;2;249;226;175m",
        "magenta": "\033[38;2;203;166;247m",
        "red": "\033[38;2;243;139;168m",
        "white": "\033[38;2;205;214;244m",
        "fzf_colors": "bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8,fg:#cdd6f4,header:#89b4fa,info:#cba6f7,pointer:#f5e0dc,marker:#b4befe,prompt:#cba6f7,hl+:#f38ba8,border:#cba6f7",
    },
    "dracula": {
        "blue": "\033[38;2;98;114;164m",
        "cyan": "\033[38;2;139;233;253m",
        "green": "\033[38;2;80;250;123m",
        "yellow": "\033[38;2;241;250;140m",
        "magenta": "\033[38;2;255;121;198m",
        "red": "\033[38;2;255;85;85m",
        "white": "\033[38;2;248;248;242m",
        "fzf_colors": "bg+:#44475a,bg:#282a36,spinner:#f8f8f2,hl:#bd93f9,fg:#f8f8f2,header:#8be9fd,info:#ffb86c,pointer:#ff79c6,marker:#50fa7b,prompt:#bd93f9,hl+:#ff79c6,border:#bd93f9",
    },
    "gruvbox": {
        "blue": "\033[38;2;131;165;152m",
        "cyan": "\033[38;2;142;192;124m",
        "green": "\033[38;2;184;187;38m",
        "yellow": "\033[38;2;250;189;47m",
        "magenta": "\033[38;2;211;134;155m",
        "red": "\033[38;2;251;73;52m",
        "white": "\033[38;2;235;219;178m",
        "fzf_colors": "bg+:#3c3836,bg:#282828,spinner:#ebdbb2,hl:#fabd2f,fg:#ebdbb2,header:#fe8019,info:#b8bb26,pointer:#fb4934,marker:#b8bb26,prompt:#fabd2f,hl+:#fb4934,border:#fe8019",
    },
    "nord": {
        "blue": "\033[38;2;129;161;193m",
        "cyan": "\033[38;2;136;192;208m",
        "green": "\033[38;2;163;190;140m",
        "yellow": "\033[38;2;235;203;139m",
        "magenta": "\033[38;2;180;142;173m",
        "red": "\033[38;2;191;97;106m",
        "white": "\033[38;2;236;239;244m",
        "fzf_colors": "bg+:#3b4252,bg:#2e3440,spinner:#eceff4,hl:#88c0d0,fg:#eceff4,header:#81a1c1,info:#ebcb8b,pointer:#88c0d0,marker:#a3be8c,prompt:#b48ead,hl+:#88c0d0,border:#88c0d0",
    },
    "monokai": {
        "blue": "\033[38;2;102;217;239m",
        "cyan": "\033[38;2;166;226;46m",
        "green": "\033[38;2;166;226;46m",
        "yellow": "\033[38;2;230;219;116m",
        "magenta": "\033[38;2;249;38;114m",
        "red": "\033[38;2;249;38;114m",
        "white": "\033[38;2;248;248;242m",
        "fzf_colors": "bg+:#3e3d32,bg:#272822,spinner:#f8f8f2,hl:#e6db74,fg:#f8f8f2,header:#66d9ef,info:#a6e22e,pointer:#f92672,marker:#a6e22e,prompt:#f92672,hl+:#fd971f,border:#66d9ef",
    },
}

_CURRENT_THEME = "default"
C_BLUE = THEMES["default"]["blue"]
C_CYAN = THEMES["default"]["cyan"]
C_GREEN = THEMES["default"]["green"]
C_YELLOW = THEMES["default"]["yellow"]
C_MAGENTA = THEMES["default"]["magenta"]
C_RED = THEMES["default"]["red"]
C_WHITE = THEMES["default"]["white"]
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"
_FZF_THEME_COLORS = THEMES["default"]["fzf_colors"]


def get_current_theme():
    return _CURRENT_THEME


def apply_theme(name):
    """Apply terminal ANSI theme and FZF color parameters."""
    global _CURRENT_THEME, C_BLUE, C_CYAN, C_GREEN, C_YELLOW, C_MAGENTA, C_RED, C_WHITE, _FZF_THEME_COLORS
    name = name.lower()
    if name not in THEMES:
        return False
    _CURRENT_THEME = name
    t = THEMES[name]
    C_BLUE = t["blue"]
    C_CYAN = t["cyan"]
    C_GREEN = t["green"]
    C_YELLOW = t["yellow"]
    C_MAGENTA = t["magenta"]
    C_RED = t["red"]
    C_WHITE = t["white"]
    _FZF_THEME_COLORS = t["fzf_colors"]
    return True
