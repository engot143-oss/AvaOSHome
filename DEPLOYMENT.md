# AVA OS Deployment Guide

Deploy AVA OS on Windows, macOS, Linux, or Docker.

## Prerequisites

- **Python 3.9+** (required for desktop/local deployment)
- **Anthropic API Key** (from https://console.anthropic.com/account/keys)
- **Docker** (optional, for containerized deployment)

## Installation

### Option 1: Automated Setup (Recommended)

Run the installation script which handles everything:

```bash
python scripts/install.py
```

This will:
1. Verify Python version
2. Install dependencies
3. Prompt for your Anthropic API key
4. Create necessary directories
5. Initialize the knowledge base

### Option 2: Manual Setup

**Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Step 2: Set Your API Key**

#### Windows (PowerShell)
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

To make it permanent, set it in Environment Variables:
1. Press `Win+X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Click "New" under "User variables"
5. Variable name: `ANTHROPIC_API_KEY`
6. Variable value: Your API key
7. Click OK

#### macOS/Linux
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

To make it permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

**Step 3: Initialize**

```bash
python scripts/manage_knowledge.py --init
```

## Running AVA OS

### Chat Interface

#### Windows
Double-click `scripts/run_chat.bat` or run from command prompt:
```bash
scripts/run_chat.bat           # Text mode
scripts/run_chat.bat --voice   # With voice I/O
```

#### macOS/Linux
```bash
chmod +x scripts/run_chat.sh
./scripts/run_chat.sh          # Text mode
./scripts/run_chat.sh --voice  # With voice I/O
```

Or use Python directly:
```bash
python -m avaos.chat          # Text mode
python -m avaos.chat --voice  # With voice I/O
```

### Parental Dashboard

#### Windows
Double-click `scripts/run_dashboard.bat` or:
```bash
scripts/run_dashboard.bat          # Default port 5000
scripts/run_dashboard.bat 8080     # Custom port
```

#### macOS/Linux
```bash
chmod +x scripts/run_dashboard.sh
./scripts/run_dashboard.sh         # Default port 5000
./scripts/run_dashboard.sh 8080    # Custom port
```

Or use Python directly:
```bash
python scripts/dashboard.py        # Default port 5000
python scripts/dashboard.py --port 8080  # Custom port
```

Then open http://localhost:5000 in your browser.

### Managing Knowledge Base

```bash
# View facts for a specific age
python scripts/manage_knowledge.py --view-age 10

# Add a new fact
python scripts/manage_knowledge.py --add

# See what's been learned
python scripts/manage_knowledge.py --learned
```

## Docker Deployment

### Single Container

**Build:**
```bash
docker build -t ava-os .
```

**Run:**
```bash
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -v ava_data:/root/.ava_os \
  ava-os
```

Then open http://localhost:5000

### Docker Compose (Recommended)

**Setup:**
```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Start the service
docker-compose up
```

**Stop:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Data persistence:**
Docker volumes `ava_memory` and `ava_knowledge` automatically persist:
- Conversation history
- Knowledge base
- Notifications

### Configure Docker

Edit `docker-compose.yml` to:
- Change port: `"5000:5000"` → `"8080:5000"`
- Add volumes for backups
- Set resource limits
- Configure networking

## Platform-Specific Notes

### Windows

**Audio Issues?**
- Install `pyaudio` separately: `pip install pyaudio`
- Check sound settings: Ensure microphone is enabled
- Try text mode first: `python -m avaos.chat`

**Environment Variables not persisting?**
- Use the GUI (see step 2 above)
- Or set in PowerShell profile: `$PROFILE`

### macOS

**Audio Issues?**
- Grant microphone permission when prompted
- Check System Preferences → Security & Privacy → Microphone
- Ensure no other apps are using the mic

**Homebrew Users:**
```bash
brew install python3
pip3 install -r requirements.txt
```

### Linux

**Audio Issues?**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Headless Mode (no audio):**
```bash
python -m avaos.chat  # Use text mode
```

### Docker on Different Platforms

**Linux with GPU:**
```yaml
# In docker-compose.yml
services:
  ava-dashboard:
    runtime: nvidia  # Requires nvidia-docker
```

**Apple Silicon (M1/M2):**
```bash
docker-compose up  # Automatically uses arm64 base image
```

**Windows with WSL2:**
```bash
# In PowerShell
wsl docker-compose up
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not found"
```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Port 5000 already in use"
```bash
# Use a different port
python scripts/dashboard.py --port 8080
```

### "Microphone not working"
```bash
# Try text mode first
python -m avaos.chat

# Then troubleshoot audio
python -c "import speech_recognition as sr; sr.Microphone().start_stream().stop_stream()"
```

### "Permission denied" on shell scripts
```bash
chmod +x scripts/run_chat.sh
chmod +x scripts/run_dashboard.sh
./scripts/run_chat.sh
```

## Data & Privacy

All data is stored locally on your machine:

- **Windows:** `%USERPROFILE%\.ava_os\`
- **macOS/Linux:** `~/.ava_os/`
- **Docker:** Named volumes (`ava_memory`, `ava_knowledge`)

### Backup

```bash
# Manual backup (all platforms)
mkdir -p backup
cp -r ~/.ava_os/* backup/

# Docker backup
docker run --rm -v ava_memory:/data -v $(pwd):/backup \
  busybox tar czf /backup/ava_backup.tar.gz -C /data .
```

### Uninstall

**Local:**
```bash
rm -rf ~/.ava_os
pip uninstall avaos
```

**Docker:**
```bash
docker-compose down -v  # -v removes volumes
docker rmi ava-os
```

## Support

- Check README.md for features and usage
- Review docs/framework_design.md for architecture
- Run tests: `python -m unittest discover -s tests`

---

Built with hallucination-checking. Questions? Check the docs or create an issue.
