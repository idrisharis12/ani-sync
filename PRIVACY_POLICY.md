# Privacy Policy for ani-sync

*Last Updated: August 31, 2026*

This Privacy Policy explains how **ani-sync** ("the Application") handles user data.

## 1. Zero Data Collection & Telemetry
**ani-sync does not collect, store, track, sell, or transmit any personal data, analytics, or telemetry to external servers.** 

All operations execute strictly on your local machine.

## 2. Local Storage of Credentials
If you connect your personal accounts:
- **MyAnimeList Tokens**: Stored locally on your machine at `~/.config/ani-sync/config.env` (or `%APPDATA%\ani-sync\config.env` on Windows).
- **Watch History**: Stored locally on your machine at `~/.config/ani-sync/history.json`.

Credentials and history files never leave your computer.

## 3. Discord Rich Presence Data
When connected to Discord, ani-sync communicates only with your **locally running Discord desktop client** via a local IPC socket / named pipe. 

The data sent consists solely of the public metadata needed to display your active status:
- Title of the anime currently playing.
- Current episode number.
- Playback elapsed time timestamp.

ani-sync does not access your Discord chats, server memberships, private messages, or account tokens.

## 4. Third-Party Links & APIs
When you sync with MyAnimeList, direct encrypted HTTPS requests are made between your computer and `api.myanimelist.net`. Please refer to [MyAnimeList Privacy Policy](https://myanimelist.net/about/privacy_policy) for information on their data handling practices.

## 5. Security & Open Source
ani-sync is 100% open-source. All code is publicly auditable at:
https://github.com/idrisharis12/ani-sync

## 6. Contact
For any privacy questions or inquiries regarding ani-sync, please open an issue on GitHub:
https://github.com/idrisharis12/ani-sync/issues
