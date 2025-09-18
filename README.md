# Reddit MCP Server

A comprehensive Model Context Protocol (MCP) server for Reddit integration. This server enables AI agents to interact with Reddit programmatically through a standardized interface.

## 🎯 Features

This MCP server provides 6 powerful tools for Reddit interaction:

- **fetchPosts** - Fetch hot posts from any subreddit
- **getComments** - Retrieve comments from specific posts
- **searchPosts** - Search for posts within subreddits
- **postComment** - Post comments on Reddit posts
- **getSubredditInfo** - Get detailed subreddit information
- **postToSubreddit** - Create new text or link posts

## 🚀 Quick Start

### Prerequisites

1. **Reddit API Credentials** - Create a Reddit app at https://www.reddit.com/prefs/apps
2. **Docker** - For containerized deployment
3. **Environment Variables**:
   - `REDDIT_CLIENT_ID` - Your Reddit app client ID
   - `REDDIT_CLIENT_SECRET` - Your Reddit app client secret
   - `REDDIT_USERNAME` - Your Reddit username
   - `REDDIT_PASSWORD` - Your Reddit password
   - `REDDIT_USER_AGENT` - User agent string (optional, defaults to "mcp-reddit-agent/0.1")

### Installation & Setup

#### Method 1: Using Docker (Recommended)

**Linux/macOS:**

```bash
# Clone the repository
git clone https://github.com/KrishnaRandad2023/mcp-reddit
cd mcp-reddit

# Build the Docker image
make build

# Set environment variables
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"

# Test the server
make test
```

**Windows (PowerShell/Batch):**

```powershell
# Clone the repository
git clone https://github.com/<my-org>/reddit-mcp
cd reddit-mcp

# Build the Docker image
.\build.ps1 build
# Or use simple batch file: .\build-win.bat build

# Set environment variables
$env:REDDIT_CLIENT_ID = "your_client_id"
$env:REDDIT_CLIENT_SECRET = "your_client_secret"
$env:REDDIT_USERNAME = "your_username"
$env:REDDIT_PASSWORD = "your_password"

# Test the server
.\build.ps1 test
# Or: .\build-win.bat test
```

#### Method 2: Using Task Commands (Docker MCP)

```bash
# Create server instance
task create -- --category social https://github.com/<my-org>/reddit-mcp \
  -e REDDIT_CLIENT_ID=your_client_id \
  -e REDDIT_USERNAME=your_username \
  -e REDDIT_USER_AGENT="mcp-reddit-agent/0.1" \
  -e REDDIT_CLIENT_SECRET=your_client_secret \
  -e REDDIT_PASSWORD=your_password

# Build the tools
task build -- --tools reddit-mcp

# Import catalog
task catalog -- reddit-mcp
docker mcp catalog import $PWD/catalogs/reddit-mcp/catalog.yaml
```

#### Method 3: Direct Docker Run

```bash
docker run --rm -i \
  -e REDDIT_CLIENT_ID="your_client_id" \
  -e REDDIT_CLIENT_SECRET="your_client_secret" \
  -e REDDIT_USERNAME="your_username" \
  -e REDDIT_PASSWORD="your_password" \
  -e REDDIT_USER_AGENT="mcp-reddit-agent/0.1" \
  mcp/reddit-mcp:latest
```

## 🛠️ Tool Reference

### fetchPosts

Fetch hot posts from a subreddit.

**Arguments:**

- `subreddit` (string, required) - Name of the subreddit
- `limit` (integer, optional) - Number of posts to fetch (1-100, default: 10)

**Example:**

```json
{
  "subreddit": "technology",
  "limit": 5
}
```

### getComments

Get comments for a specific Reddit post.

**Arguments:**

- `post_id` (string, required) - Reddit post ID (without 't3\_' prefix)

**Example:**

```json
{
  "post_id": "abc123"
}
```

### searchPosts

Search for posts within a subreddit.

**Arguments:**

- `subreddit` (string, required) - Name of the subreddit
- `query` (string, required) - Search query
- `limit` (integer, optional) - Number of results (1-100, default: 10)

**Example:**

```json
{
  "subreddit": "programming",
  "query": "python tutorial",
  "limit": 10
}
```

### postComment

Post a comment on a Reddit post.

**Arguments:**

- `post_id` (string, required) - Reddit post ID (without 't3\_' prefix)
- `comment_text` (string, required) - Comment text to post

**Example:**

```json
{
  "post_id": "abc123",
  "comment_text": "Great post! Thanks for sharing."
}
```

### getSubredditInfo

Get detailed information about a subreddit.

**Arguments:**

- `subreddit` (string, required) - Name of the subreddit

**Example:**

```json
{
  "subreddit": "MachineLearning"
}
```

### postToSubreddit

Create a new post in a subreddit.

**Arguments:**

- `subreddit` (string, required) - Name of the subreddit
- `title` (string, required) - Post title
- `content` (string, optional) - Post content for text posts
- `url` (string, optional) - URL for link posts

**Note:** Either `content` or `url` must be provided.

**Example (Text Post):**

```json
{
  "subreddit": "test",
  "title": "My Test Post",
  "content": "This is a test post created via MCP."
}
```

**Example (Link Post):**

```json
{
  "subreddit": "technology",
  "title": "Interesting Article",
  "url": "https://example.com/article"
}
```

## 🔧 Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/<my-org>/reddit-mcp
cd reddit-mcp

# Install dependencies
pip install -r requirements.txt

# Run locally (requires environment variables)
python src/server.py
```

### Available Build Commands

**Linux/macOS (Makefile):**

```bash
make help       # Show help
make build      # Build Docker image
make test       # Run tests
make catalog    # Generate MCP catalog
make publish    # Prepare for registry submission
make clean      # Clean up Docker images
```

**Windows (PowerShell/Batch):**

```powershell
.\build.ps1 help       # Show help
.\build.ps1 build      # Build Docker image
.\build.ps1 test       # Run tests
.\build.ps1 catalog    # Generate MCP catalog
.\build.ps1 publish    # Prepare for registry submission
.\build.ps1 clean      # Clean up Docker images

# Or use simple batch files:
.\build-win.bat build       # Build Docker image
.\build-win.bat test        # Run tests
.\build-win.bat catalog     # Generate MCP catalog
.\build-win.bat clean       # Clean up Docker images
```

### Project Structure

```
reddit-mcp/
├── src/
│   └── server.py          # Main MCP server implementation
├── catalogs/
│   └── reddit-mcp/
│       └── catalog.yaml   # MCP catalog definition
├── Dockerfile             # Docker container definition
├── requirements.txt       # Python dependencies
├── server.json           # MCP server metadata
├── tools.json            # Tool definitions
├── Makefile              # Build automation
├── *.sh                  # Shell scripts for automation
└── README.md             # This file
```

## 🔐 Security & Authentication

### Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note your client ID (under app name) and client secret
5. Set environment variables with your credentials

### Environment Variables

| Variable               | Required | Secret | Description                                         |
| ---------------------- | -------- | ------ | --------------------------------------------------- |
| `REDDIT_CLIENT_ID`     | ✅       | ❌     | Reddit application client ID                        |
| `REDDIT_CLIENT_SECRET` | ✅       | ✅     | Reddit application client secret                    |
| `REDDIT_USERNAME`      | ✅       | ❌     | Your Reddit username                                |
| `REDDIT_PASSWORD`      | ✅       | ✅     | Your Reddit password                                |
| `REDDIT_USER_AGENT`    | ❌       | ❌     | User agent string (default: "mcp-reddit-agent/0.1") |

### Security Best Practices

- Store secrets securely (use environment variables, not hardcoded values)
- Use dedicated Reddit account for automation
- Follow Reddit's API rate limiting guidelines
- Respect subreddit rules and Reddit's terms of service

## 📋 Usage Examples

### Example Claude Desktop Configuration

```json
{
  "mcpServers": {
    "reddit": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "REDDIT_CLIENT_ID=your_client_id",
        "-e",
        "REDDIT_CLIENT_SECRET=your_client_secret",
        "-e",
        "REDDIT_USERNAME=your_username",
        "-e",
        "REDDIT_PASSWORD=your_password",
        "-e",
        "REDDIT_USER_AGENT=mcp-reddit-agent/0.1",
        "mcp/reddit-mcp:latest"
      ]
    }
  }
}
```

### Example Conversations

**Fetch Latest Posts:**

> "Get the top 5 posts from r/technology"

**Search and Comment:**

> "Search for Python tutorials in r/programming and comment on the top result"

**Subreddit Analysis:**

> "Get information about r/MachineLearning and show me recent posts about transformers"

## 🚀 Deployment & Submission

### Docker Registry Submission

This server is ready for submission to the official Docker MCP Registry:

1. **Build and test locally:**

   **Linux/macOS:**

   ```bash
   make build
   make test
   ```

   **Windows:**

   ```powershell
   .\build.ps1 build
   .\build.ps1 test
   ```

2. **Push to Docker Hub:**

   ```bash
   docker tag mcp/reddit-mcp:latest your-dockerhub-username/reddit-mcp:latest
   docker push your-dockerhub-username/reddit-mcp:latest
   ```

3. **Update server.json with your repository details**

4. **Submit to MCP Registry:**
   ```bash
   # Using mcp-publisher CLI
   mcp-publisher init
   mcp-publisher login github
   mcp-publisher publish
   ```

### MCP Registry Requirements ✅

This server meets all Docker MCP registry requirements:

- ✅ **Docker Label**: `io.modelcontextprotocol.server.name="reddit-mcp"`
- ✅ **STDIO Transport**: Uses stdio for MCP communication
- ✅ **Environment Variables**: Properly configured secrets and env vars
- ✅ **Server Metadata**: Complete server.json with tools definitions
- ✅ **Documentation**: Comprehensive README and usage examples
- ✅ **Category**: Social (as specified)

### Registry Metadata

- **Name**: `io.github.my-org/reddit-mcp`
- **Category**: social
- **Docker Image**: `mcp/reddit-mcp`
- **Description**: Reddit MCP server for API interactions: fetch posts, search, comments, and submissions
- **Icon**: https://www.redditinc.com/assets/images/site/reddit-logo.png
- **Repository**: https://github.com/<my-org>/reddit-mcp

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/<my-org>/reddit-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/<my-org>/reddit-mcp/discussions)
- **Documentation**: [MCP Documentation](https://modelcontextprotocol.io/)
- **Reddit API**: [Reddit API Documentation](https://www.reddit.com/dev/api/)

## ⚠️ Rate Limiting & Best Practices

- Reddit API has rate limits - respect them
- Use appropriate delay between requests for bulk operations
- Follow Reddit's [API Terms of Service](https://www.redditinc.com/policies/developer-terms)
- Be respectful to communities and follow subreddit rules
- Consider using read-only operations when possible

---

**Ready for MCP Registry Submission** 🚀

This server is fully configured and ready to be submitted to the official Docker MCP Registry following all contribution guidelines.
