# ani‑sync

A tiny **command‑line wrapper** around [ani‑cli](https://github.com/pystardust/ani-cli) that automatically syncs the watched episode to **MyAnimeList** (MAL).

## Features
- Search‑and‑play anime directly from the terminal using `ani-cli`.
- After playback finishes, the script marks the episode as *watched* on your MAL account.
- No credentials are stored in the repository – use environment variables (`MAL_CLIENT_ID`, `MAL_CLIENT_SECRET`, `MAL_REFRESH_TOKEN`).
- Works with any player (`mpv` is default, but you can specify another).

## Installation
```bash
# Install dependencies
pip install --user ani-cli requests tqdm
# (optional) Install mal‑cli to obtain a refresh token
yay -S mal-cli   # or `cargo install mal-cli`
```

## Set up MyAnimeList OAuth
1. Create an application on the MAL developer portal: <https://myanimelist.net/apiconfig>
2. Fill the form (see the accompanying documentation). Use a redirect URL of `http://localhost`.
3. Authorize the app with `mal auth` to obtain a **refresh token**.
4. Export the credentials in your shell (add to `~/.bashrc` or `~/.zshrc`):
   ```bash
   export MAL_CLIENT_ID="<your‑client‑id>"
   export MAL_CLIENT_SECRET="<your‑client‑secret>"
   export MAL_REFRESH_TOKEN="$(jq -r .refresh_token ~/.config/mal-cli/token.json)"
   ```

## Usage
```bash
ani-sync watch <episode‑url> [--player mpv]
```
The script will:
1. Resolve the stream URL with `ani-cli`.
2. Launch the chosen media player (blocking until playback ends).
3. Mark the episode as watched on MAL.

## Example
```bash
ani-sync watch https://gogoanime.cm/one-piece-episode-1000 --player mpv
```

## Contributing
Feel free to open issues or submit pull‑requests. The project follows the **MIT License**.
# ani-sync
