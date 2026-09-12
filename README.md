# Save Live Captions

**Tired of losing live captions on Windows?** This is a simple tool to save the content of live captions! The saved text document is like following:

> <img width="1187" height="477" alt="image" src="https://github.com/user-attachments/assets/78f3a0df-80f3-4e40-bc0e-9137910352c6" />

### Features

- ✨ Save live captions to a text file.
- 😃 Minimalist floating dashboard.
- 📝 Captions are saved without timestamps, duplicate suppression, minimum-length filtering, or text rewriting. Each displayed caption occurrence is saved after it appears in three consecutive reads. Whitespace cleanup and punctuation-based sentence boundaries are applied; decimal numbers remain intact.

### Installation

### Option 1: Quick Start (Executable)

You can download the latest version from the [Releases](../../releases) page.

> [!IMPORTANT]
> **Note on Antivirus Alerts:** If you encounter a malware warning for the `.exe` file, it is likely a **false positive** due to the lack of a digital signature. If you worry about this, try option 2 as follows.

### Option 2: Run from Source (Recommended for Security)

If you prefer to run the code directly, follow these steps in your bash/PowerShell/cmd:

1. **Clone this repo**:

   ```bash
   git clone https://github.com/LiveCaptionsHelper/SaveLiveCaptions.git
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the tool**:

   ```bash
   python src/main.py
   ```

### Guidelines

1. Before you open this application, make sure you already **open the live captions on Windows** (or it will exit automatically). Then double click the `SaveLiveCaptions.exe`. A small dashboard will appear in the top-left corner of your screen. You can drag the background to move this window.

![Dashboard Preview](./assets/dashboard.png)

2. The **● (Circle)** button is "start to save captions" and the **■ (Square)** button is "stop and exit the application".

3. **Start saving:** When you click the circle button, a file dialog will open to choose a save location. If you don't choose the direction, the default location is `~/Documents/captions`.

4. **Stop and exit:** When you click the square button, it stops and exits the application. You can find the caption text file in the chosen location.

![Captions File Example](./assets/captionsFile.png)

## License

This project is licensed under the MIT License.
