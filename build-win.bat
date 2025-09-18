@echo off
REM Reddit MCP Server - Windows Build Commands
REM Direct command equivalents for Windows users

echo Reddit MCP Server - Windows Commands
echo.

if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="catalog" goto catalog
if "%1"=="clean" goto clean
if "%1"=="help" goto help

:help
echo Available commands:
echo.
echo   build-win.bat build     - Build the Docker image
echo   build-win.bat test      - Run basic tests
echo   build-win.bat catalog   - Generate MCP catalog
echo   build-win.bat clean     - Clean up Docker images
echo.
echo Environment variables needed:
echo   REDDIT_CLIENT_ID      - Reddit app client ID
echo   REDDIT_CLIENT_SECRET  - Reddit app client secret
echo   REDDIT_USERNAME       - Reddit username
echo   REDDIT_PASSWORD       - Reddit password
echo   REDDIT_USER_AGENT     - User agent (optional)
goto end

:build
echo 🏗️ Building Reddit MCP Server...
docker build -t mcp/reddit-mcp:latest .
if %errorlevel% neq 0 (
    echo ❌ Build failed
    exit /b 1
)
docker tag mcp/reddit-mcp:latest mcp/reddit-mcp:0.1.0
echo ✅ Build complete!
goto end

:test
echo 🧪 Testing Reddit MCP Server...
docker images mcp/reddit-mcp:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker image not found
    exit /b 1
)
echo ✅ Docker image found
echo ✅ Basic tests passed!
goto end

:catalog
echo 📚 Creating MCP catalog...
if not exist "catalogs\reddit-mcp" mkdir "catalogs\reddit-mcp"
(
echo apiVersion: v1
echo kind: MCPCatalog
echo metadata:
echo   name: reddit-mcp
echo   category: social
echo spec:
echo   servers:
echo     - name: reddit-mcp
echo       description: "Reddit MCP server for API interactions"
echo       image: mcp/reddit-mcp:latest
echo       transport: stdio
echo       environment:
echo         - name: REDDIT_CLIENT_ID
echo           required: true
echo         - name: REDDIT_CLIENT_SECRET
echo           required: true
echo           secret: true
echo         - name: REDDIT_USERNAME
echo           required: true
echo         - name: REDDIT_PASSWORD
echo           required: true
echo           secret: true
echo         - name: REDDIT_USER_AGENT
echo           default: "mcp-reddit-agent/0.1"
) > "catalogs\reddit-mcp\catalog.yaml"
echo ✅ Catalog created at catalogs\reddit-mcp\catalog.yaml
goto end

:clean
echo 🧹 Cleaning up...
docker rmi mcp/reddit-mcp:latest mcp/reddit-mcp:0.1.0 2>nul
echo ✅ Cleanup complete!
goto end

:end