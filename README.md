# NiceThings

You’ve got great taste in music. Spotify knows it. Its algorithms have mapped every song you’ve loved, skipped, or looped. But here’s the truth: preference isn’t the same as purpose.

A playlist of your favorite tracks doesn’t mean it’ll carry you through a 45-minute workout or a deep-focus study session. That’s not what algorithms are built for. They optimize for what you like — not how you want to feel.

Nice Things changes that.

We build playlists with intention. Inspired by the structure of DJ sets and film scores, each mix is crafted to follow a natural arc: easing you in, building energy, peaking at the perfect moment, then cooling down. We use detailed audio analysis — tempo, energy, mood, and more — to guide every phase.

You pick the activity, vibe, and duration. We generate a fresh, purpose-built playlist every time. No account. No shuffle chaos. No repeats.

**Visit our website: [nicethings.wtf](https://nicethings.wtf)**
(Optional) Download the live version as a PWA mobile app

## 🚀 Getting Started

This project is managed with a `Makefile` to simplify setup and development.

### Prerequisites

- **docker**
- **Python 3.13+**
- **uv** (Python package manager)
- **Node.js** (v22.17.0 recommended)
- **nvm** (for easy install of exact node version)
- **Git**

### Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2.  **Install all dependencies:**
    This command will install both backend (Python) and frontend (Node.js) dependencies.
    ```bash
    make install
    ```

### Running the Application

-   **Start both development servers (backend and frontend):**
    ```bash
    docker compose up -d
    ```
 
    ```bash
    make dev
    ```
    -   **Frontend:** Available at `http://localhost:3000`
    -   **Backend API:** Available at `http://localhost:8000`

## 🛠️ Development Commands

All common tasks are available as `make` commands. Run `make help` to see a full list of available commands.

| Command         | Description                                     |
| --------------- | ----------------------------------------------- |
| `make install`  | Install all backend and frontend dependencies   |
| `make dev`      | Start both development servers                  |
| `make build`    | Build the application for production            |
| `make test`     | Run all tests                                   |
| `make lint`     | Lint all code                                   |
| `make format`   | Format all code                                 |

## 📁 Project Structure

```
.
├── backend/      # FastAPI backend
├── frontend/     # React frontend
├── Makefile      # Development commands
└── README.md     # This file
```

## 🔧 Technology Stack

-   **Backend:** FastAPI, Python 3.13+, Uvicorn
-   **Frontend:** React, TypeScript, Vite, Shadcn, Tailwind CSS, Tanstack Router+Query+Form
-   **Package Management:** `uv` (Python), `npm` (Node.js)
