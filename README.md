# 🔎 PoliScan

To get started, ensure you have Git installed and clone the repository:

```sh
git clone https://github.com/ohmrr/poli-scan.git
cd poli-scan
```

## 🖥️ Development Environment

Before setting up either the backend or frontend, make sure your system is ready.

**Windows users** are strongly recommended to use **WSL (Windows Subsystem for Linux)**. While it is not strictly required, most tooling in this project works reliably in a Unix-like environment.

Mac and Linux users should be fine to proceed as-is.

## ⚙️ Backend Setup

### 📋 Prerequisites

- **Python** version `3.12.12`
- Ollama (see below)

### 🦙 Installing and Running Ollama

Ollama is required, in development, to run the local LLM used for conflict-of-interest matching.

Install **Ollama** and follow the [instructions](https://ollama.com/download) for your operating system.

Once installed, pull the model. If your machine can handle it, use the default:

```sh
ollama pull qwen2.5:14b
```

If your machine struggles, you may try a smaller model. Note that these models will have less accuracy.

```sh
ollama pull qwen2.5:7b

# or

ollama pull qwen2.5:3b
```

> [!TIP]
> Make sure to update `OLLAMA_MODEL` in your `.env` to match whichever model you end up using.

#### 🔧 Running the Ollama Service

Start the Ollama service in a separate terminal so that it runs in the background.

```sh
ollama serve
```

> [!NOTE]
> On macOS, Linux, or WSL, Ollama may start automatically after installation. You can verify that it's running by visiting http://127.0.0.1:11434 in your browser.

### 💾 Setting up Python Virtual Environment

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

> [!TIP]
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

> [!INFO]
> This ensures that we all use the same package versions.

#### ⬇️ Adding New Dependencies

Note that whenever you add a new package, update `requirement.txt`:

```sh
pip freeze > server/requirements.txt
```

### 🔑 Adding Environment Variables

In `/server`, make a new file called `.env` and copy over the contents of `.env.example`. For the actual environment variable values themselves, you can reach out to Omar and ask for them.

```sh
ENV='development' # development | production

OLLAMA_BASE_URL='http://127.0.0.1:11434'
OLLAMA_MODEL='qwen2.5:14b'

TURSO_DATABASE_URL='libsql://{db-name}-{owner-name}.{server}.turso.io'
TURSO_AUTH_TOKEN=''
```

> [!WARNING]
> You should never expose the contents of `.env` for any reason. Do not include them in source control and push them to GitHub, or copy and paste them to ChatGPT or any other LLM. Please keep them secure and private.


### ▶️ Running the FastAPI Server

From the root directory `poli-scan/`, run:

```sh
uvicorn server.app.main:app --reload
```

The server will now be accessible at `http://127.0.0.1:8000/`

You can open Swagger API documentation by going to `http://127.0.0.1:8000/docs`, which will help with testing out the API.

## 🌐 Frontend Setup

### 📋 Prerequisites

- Install [Node.js](https://nodejs.org/en/download), you can get the latest LTS version which is `v24.14.0`

Installation varies depending on what device you're using. See the link above for more details.

Following installation, you can confirm that it is properly installed and set up by using:

```sh
node --version
npm --version
```

### 📦 Installing Dependencies

Once you have `node` set up, you can move to the `website` directory and install all the dependencies needed for the project.

First, enable corepack and install the `pnpm` package manager:

```sh
corepack enable
corepack install -g pnpm
```

```sh
cd website
pnpm install
```

#### ⬇️ Adding New Dependencies

Whenever you need to install a new package, you can use `npm` to save the package and its version to `website/package.json`.

For production packages, such as `tailwindcss`, you can run:

```sh
pnpm install [package]
```

For development packages, such as `prettier`, you can instead run:

```sh
pnpm install --dev [package]
```

> [!NOTE]
> Whenever you install packages, ensure that you are working in the `website` directory

### ▶️ Running the Website

With the project configured, you can run the following:

```sh
pnpm dev
```

This will spin up a development server with the website that will automatically update with any changes.

The development site will now be accessible at `http://localhost:5173/`
