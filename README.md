# 🔎 PoliScan

To get started, ensure you have Git installed and clone the repository:

```sh
git clone https://github.com/ohmrr/poli-scan.git
cd poli-scan
```

## ⚙️ Backend Setup

### 📋 Prerequisites

- Install **Python** version `3.12.12`

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

### 🔑 Adding Database Credentials

In `/server`, make a new file called `.env` and copy over the contents of `.env.example`. For the actual environment variable values themselves, you can reach out to Omar and ask for them.

```sh
TURSO_DATABASE_URL=libsql://{db-name}-{owner-name}.{server}.turso.io
TURSO_AUTH_TOKEN=
```

**NOTE**: You should never expose the contents of `.env` for any reason. Do not include them in source control and push them to GitHub, or copy and paste them to ChatGPT or any other LLM. Please keep them secure and private.


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

*Note: Whenever you install packages, ensure that you are working in the `website` directory*

### ▶️ Running the Website

With the project configured, you can run the following:

```sh
pnpm dev
```

This will spin up a development server with the website that will automatically update with any changes.

The development site will now be accessible at `http://localhost:5173/`
