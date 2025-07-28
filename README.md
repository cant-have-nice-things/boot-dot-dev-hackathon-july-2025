# NiceThings

**Visit our website: [nicethings.xyz](https://nicethings.xyz)**

NiceThings is a full-stack application that generates personalized Spotify playlists based on your activity and desired vibe. Whether you're coding, working out, or just relaxing, NiceThings creates the perfect soundtrack for your moment.

## 🚀 Getting Started

This project is managed with a `Makefile` to simplify setup and development.

### Prerequisites

- **Python 3.13+**
- **uv** (Python package manager)
- **Node.js** (v18+ recommended)
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
-   **Frontend:** React, TypeScript, Vite, Tailwind CSS
-   **Package Management:** `uv` (Python), `npm` (Node.js)
