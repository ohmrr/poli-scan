# 🔎 PoliScan

To get started, ensure you have Git installed and clone the repository:

```sh
git clone https://github.com/ohmrr/poli-scan.git
cd poli-scan
```

## ⚙️ Backend Setup

### 📋 Prerequisites

- Install Python version `3.12.12`

### 💾 Setting up Virtual Environment

Create a virtual environment. You only have to do this once per system.

```sh
python -m venv server/venv
```

#### ⚡ Activating Virtual Environment

macOS/Linux/Windows Subsystem for Linux

```sh
source server/venv/bin/activate
```

Windows (PowerShell)

```powershell
server\venv\Scripts\Activate.ps1
```

> When activated, your terminal prompt should show (venv).

If you wish to deactivate the virtual environment, simply run:

```sh
deactivate
```

### 📦 Installing Dependencies

With the venv activated, install the required Python packages from the `server/requirements.txt` file.

```sh
pip install -r server/requirements.txt
```

> This ensures that we all use the same package versions.

#### ⬇️ Adding New Dependencies

Note that whenever you add a new package, update `requirement.txt`:

```sh
pip freeze > server/requirements.txt
```

### ▶️ Running the FastAPI Server

From the root directory `poli-scan/`, run:

```sh
uvicorn server.app.main:app --reload
```

The server will now be accessible at `http://127.0.0.1:8000/` to see:

```json
{ "message": "App is running successfully!" }
```
