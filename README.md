# Boot.dev Hackathon Project - July 2025

> **Note:** This project is currently in development. Specific features and functionality will be documented as they are implemented.

## 🏗️ Project Structure

This is a full-stack application with:
- **Backend**: FastAPI application (Python 3.13+) with `uv` for dependency management
- **Frontend**: React/Next.js application with TypeScript

## 📋 Prerequisites

Before you can run this project, you'll need to install the following tools:

### Required Dependencies

1. **Python 3.13+**
    - Download from [python.org](https://www.python.org/downloads/)
    - Verify installation: `python --version`

2. **uv** (Python package manager)
   ```bash
   # Install uv (recommended method)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Alternative: using pip
   pip install uv
   
   # Alternative: using Homebrew (macOS)
   brew install uv
   
   # Alternative: using winget (Windows)
   winget install astral-sh.uv
   ```
    - Verify installation: `uv --version`
    - Documentation: [uv.readthedocs.io](https://uv.readthedocs.io/)

3. **Node.js** (v18+ recommended)
    - **Option A**: Direct install from [nodejs.org](https://nodejs.org/)
    - **Option B**: Using nvm (recommended for version management)
      ```bash
      # Install nvm
      curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
      
      # Install and use Node.js v20 (or latest LTS)
      nvm install 22.17.0
      nvm use 22.17.0
      ```
    - Verify installation: `node --version` and `npm --version`

4. **Git** (for version control)
    - Download from [git-scm.com](https://git-scm.com/)

### Quick Dependency Check

Run this command to verify all required tools are installed:
```bash
make check-deps
```

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Install Dependencies
```bash
# Install all dependencies (backend + frontend)
make install

# Or install separately:
make install-backend   # Install Python dependencies
make install-frontend  # Install Node.js dependencies
```

### 3. Start Development Servers
```bash
# Start both backend and frontend development servers
make dev

# Or start separately:
make dev-backend   # Start FastAPI server (http://localhost:8000)
make dev-frontend  # Start React/Next.js server (http://localhost:3000)
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## 🛠️ Development Commands

### Essential Commands
| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install all dependencies |
| `make dev` | Start development servers |
| `make build` | Build for production |
| `make test` | Run all tests |
| `make lint` | Run code linting |
| `make format` | Format code |
| `make clean` | Clean build artifacts |

### Backend Commands
| Command | Description |
|---------|-------------|
| `make install-backend` | Install Python dependencies |
| `make dev-backend` | Start FastAPI development server |
| `make build-backend` | Build backend for production |
| `make test-backend` | Run backend tests |
| `make lint-backend` | Lint Python code with Ruff |
| `make format-backend` | Format Python code with Ruff |

### Frontend Commands
| Command | Description |
|---------|-------------|
| `make install-frontend` | Install Node.js dependencies |
| `make dev-frontend` | Start React/Next.js development server |
| `make build-frontend` | Build frontend for production |
| `make test-frontend` | Run frontend tests |
| `make lint-frontend` | Lint TypeScript/JavaScript code |
| `make format-frontend` | Format frontend code |

## 📁 Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   └── main.py        # FastAPI app entry point
│   ├── pyproject.toml     # Python dependencies (uv)
│   └── .gitignore         # Backend-specific gitignore
├── frontend/              # React/Next.js frontend
│   ├── src/              # Source code
│   ├── package.json      # Node.js dependencies
│   ├── package-lock.json # Locked dependencies
│   └── .gitignore        # Frontend-specific gitignore
├── Makefile              # Development commands
├── .gitignore           # Project-wide gitignore
└── README.md            # This file
```

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **Package Manager**: uv
- **Server**: Uvicorn
- **Environment**: python-dotenv

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite/Next.js
- **Package Manager**: npm
- **UI Components**: Radix UI
- **Styling**: Tailwind CSS (likely)

## 🔍 Development Tips

### Backend Development
- The backend uses `uv` for fast Python package management
- API server runs on http://localhost:8000 with auto-reload enabled
- Visit http://localhost:8000/docs for interactive API documentation

### Frontend Development
- Frontend development server includes hot reloading
- TypeScript is configured for type safety
- ESLint is set up for code quality

### Using nvm for Node.js Version Management
If you're using nvm, you can create a `.nvmrc` file in the project root:
```bash
echo "20" > .nvmrc  # or your preferred Node.js version
nvm use            # Automatically use the correct version
```

## 🐛 Troubleshooting

### Common Issues

1. **"uv command not found"**
    - Make sure uv is installed and in your PATH
    - Try restarting your terminal after installation

2. **"Node.js version mismatch"**
    - Use nvm to install and switch to the correct Node.js version
    - Check `frontend/.nvmrc` file

3. **Port already in use**
    - Backend (8000): `lsof -ti:8000 | xargs kill -9`
    - Frontend (3000): `lsof -ti:3000 | xargs kill -9`

4. **Permission errors on Unix/macOS**
    - Make sure the Makefile has proper line endings (LF, not CRLF)
    - Check file permissions: `chmod +x Makefile`

### Getting Help
- Run `make help` to see all available commands
- Check the specific tool documentation:
    - [uv documentation](https://uv.readthedocs.io/)
    - [FastAPI documentation](https://fastapi.tiangolo.com/)
    - [Node.js documentation](https://nodejs.org/docs/)

## 📝 Next Steps

This README will be updated as the project develops with:
- Specific feature documentation
- API endpoint descriptions
- Deployment instructions
- Contributing guidelines
- Environment variable configuration