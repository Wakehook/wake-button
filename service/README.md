# Run the agent in the background

Pick the file for your system. Each one keeps the hook address in the service's environment, so it isn't in your shell history or the repository. Edit the paths and the `REPLACE_ME` address first.

| System | File | Install |
|---|---|---|
| Linux (systemd) | [`wake-button.service`](wake-button.service) | `sudo cp wake-button.service /etc/systemd/system/ && sudo systemctl enable --now wake-button` |
| macOS (launchd) | [`com.wakehook.wake-button.plist`](com.wakehook.wake-button.plist) | `cp com.wakehook.wake-button.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.wakehook.wake-button.plist` |
| Windows | [`install-windows.ps1`](install-windows.ps1) | Run it in PowerShell; it adds a task that starts at sign-in |

On Linux, the user running the agent needs access to the serial port: `sudo usermod -aG dialout $USER`, then sign out and back in.

Make the env file or plist readable only by you (`chmod 600`): it holds the hook address.
