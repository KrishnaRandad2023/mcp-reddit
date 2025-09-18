#!/usr/bin/env python3
"""
Reddit MCP Server

A Model Context Protocol server for Reddit integration.
Provides tools to interact with Reddit API programmatically.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any

import praw
import prawcore
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

# Global Reddit client
reddit = None

def initialize_reddit():
    """Initialize Reddit client with proper error handling for different app types"""
    global reddit
    
    try:
        # First try script app authentication (password auth)
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "mcp-reddit-agent/0.1"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
        
        # Test the connection
        reddit.user.me()
        logger.info("Reddit client initialized successfully with password auth")
        
    except prawcore.exceptions.OAuthException as oauth_error:
        if "Only script apps may use password auth" in str(oauth_error):
            logger.warning("Password auth failed - your Reddit app must be a 'script' type app")
            logger.warning("Please create a new Reddit app at https://www.reddit.com/prefs/apps")
            logger.warning("Select 'script' as the app type to use password authentication")
            logger.warning("Trying read-only mode instead...")
            try:
                # Fall back to read-only mode for non-script apps
                reddit = praw.Reddit(
                    client_id=os.getenv("REDDIT_CLIENT_ID"),
                    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                    user_agent=os.getenv("REDDIT_USER_AGENT", "mcp-reddit-agent/0.1"),
                )
                logger.info("Reddit client initialized in read-only mode")
                logger.warning("Note: Post and comment creation will not work without a script app")
            except Exception as fallback_error:
                logger.error(f"Failed to initialize Reddit client in read-only mode: {fallback_error}")
                raise
        else:
            logger.error(f"Reddit OAuth error: {oauth_error}")
            raise
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}")
        raise

# Initialize the MCP server
app = Server("reddit-mcp")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available Reddit tools"""
    return [
        types.Tool(
            name="fetchPosts",
            description="Fetch hot posts from a subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Name of the subreddit"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to fetch (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                },
                "required": ["subreddit"]
            }
        ),
        types.Tool(
            name="getComments",
            description="Get comments for a specific Reddit post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID (without 't3_' prefix)"
                    }
                },
                "required": ["post_id"]
            }
        ),
        types.Tool(
            name="searchPosts",
            description="Search for posts within a subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Name of the subreddit"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                },
                "required": ["subreddit", "query"]
            }
        ),
        types.Tool(
            name="postComment",
            description="Post a comment on a Reddit post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID (without 't3_' prefix)"
                    },
                    "comment_text": {
                        "type": "string",
                        "description": "Comment text to post"
                    }
                },
                "required": ["post_id", "comment_text"]
            }
        ),
        types.Tool(
            name="getSubredditInfo",
            description="Get information about a subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Name of the subreddit"
                    }
                },
                "required": ["subreddit"]
            }
        ),
        types.Tool(
            name="postToSubreddit",
            description="Create a new post in a subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Name of the subreddit"
                    },
                    "title": {
                        "type": "string",
                        "description": "Post title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Post content (for text posts)"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL (for link posts)"
                    }
                },
                "required": ["subreddit", "title"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls"""
    if not reddit:
        return [types.TextContent(
            type="text",
            text="Error: Reddit client not initialized. Please check your credentials."
        )]
    
    try:
        if name == "fetchPosts":
            return await fetch_posts(arguments or {})
        elif name == "getComments":
            return await get_comments(arguments or {})
        elif name == "searchPosts":
            return await search_posts(arguments or {})
        elif name == "postComment":
            return await post_comment(arguments or {})
        elif name == "getSubredditInfo":
            return await get_subreddit_info(arguments or {})
        elif name == "postToSubreddit":
            return await post_to_subreddit(arguments or {})
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def fetch_posts(args: dict[str, Any]) -> list[types.TextContent]:
    """Fetch hot posts from a subreddit"""
    subreddit_name = args.get("subreddit")
    limit = min(args.get("limit", 10), 100)
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        for submission in subreddit.hot(limit=limit):
            post_data = {
                "id": submission.id,
                "title": submission.title,
                "author": str(submission.author) if submission.author else "[deleted]",
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "url": submission.url,
                "permalink": f"https://reddit.com{submission.permalink}",
                "created_utc": submission.created_utc,
                "num_comments": submission.num_comments,
                "is_self": submission.is_self,
                "selftext": submission.selftext[:500] + "..." if len(submission.selftext) > 500 else submission.selftext,
                "flair": submission.link_flair_text
            }
            posts.append(post_data)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({"posts": posts, "subreddit": subreddit_name}, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error fetching posts from r/{subreddit_name}: {str(e)}"
        )]

async def get_comments(args: dict[str, Any]) -> list[types.TextContent]:
    """Get comments for a specific post"""
    post_id = args.get("post_id")
    
    try:
        submission = reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)  # Remove "more comments" objects
        
        comments = []
        for comment in submission.comments.list():
            if hasattr(comment, 'body'):  # Skip deleted comments
                comment_data = {
                    "id": comment.id,
                    "author": str(comment.author) if comment.author else "[deleted]",
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": comment.created_utc,
                    "parent_id": comment.parent_id,
                    "depth": comment.depth if hasattr(comment, 'depth') else 0
                }
                comments.append(comment_data)
        
        post_info = {
            "id": submission.id,
            "title": submission.title,
            "author": str(submission.author) if submission.author else "[deleted]",
            "score": submission.score,
            "url": submission.url,
            "permalink": f"https://reddit.com{submission.permalink}"
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps({"post": post_info, "comments": comments}, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error getting comments for post {post_id}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting comments for post {post_id}: {str(e)}"
        )]

async def search_posts(args: dict[str, Any]) -> list[types.TextContent]:
    """Search for posts within a subreddit"""
    subreddit_name = args.get("subreddit")
    query = args.get("query")
    limit = min(args.get("limit", 10), 100)
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        for submission in subreddit.search(query, limit=limit):
            post_data = {
                "id": submission.id,
                "title": submission.title,
                "author": str(submission.author) if submission.author else "[deleted]",
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "url": submission.url,
                "permalink": f"https://reddit.com{submission.permalink}",
                "created_utc": submission.created_utc,
                "num_comments": submission.num_comments,
                "is_self": submission.is_self,
                "selftext": submission.selftext[:300] + "..." if len(submission.selftext) > 300 else submission.selftext,
                "flair": submission.link_flair_text
            }
            posts.append(post_data)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "posts": posts, 
                "subreddit": subreddit_name, 
                "query": query,
                "results_count": len(posts)
            }, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error searching r/{subreddit_name} for '{query}': {e}")
        return [types.TextContent(
            type="text",
            text=f"Error searching r/{subreddit_name} for '{query}': {str(e)}"
        )]

async def post_comment(args: dict[str, Any]) -> list[types.TextContent]:
    """Post a comment on a Reddit post"""
    post_id = args.get("post_id")
    comment_text = args.get("comment_text")
    
    # Check if we have write permissions
    try:
        reddit.user.me()  # This will fail if we're in read-only mode
    except:
        return [types.TextContent(
            type="text",
            text="Error: Cannot post comments. Reddit app must be a 'script' type app for write operations."
        )]
    
    try:
        submission = reddit.submission(id=post_id)
        comment = submission.reply(comment_text)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "comment_id": comment.id,
                "comment_url": f"https://reddit.com{comment.permalink}",
                "post_title": submission.title,
                "post_url": f"https://reddit.com{submission.permalink}"
            }, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error posting comment to {post_id}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error posting comment to post {post_id}: {str(e)}"
        )]

async def get_subreddit_info(args: dict[str, Any]) -> list[types.TextContent]:
    """Get information about a subreddit"""
    subreddit_name = args.get("subreddit")
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        subreddit_info = {
            "name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.description,
            "subscribers": subreddit.subscribers,
            "active_users": subreddit.active_user_count,
            "created_utc": subreddit.created_utc,
            "over18": subreddit.over18,
            "public_description": subreddit.public_description,
            "url": f"https://reddit.com/r/{subreddit.display_name}",
            "rules": []
        }
        
        # Get subreddit rules
        try:
            for rule in subreddit.rules():
                subreddit_info["rules"].append({
                    "short_name": rule.short_name,
                    "description": rule.description,
                    "kind": rule.kind
                })
        except:
            pass  # Rules might not be accessible
        
        return [types.TextContent(
            type="text",
            text=json.dumps(subreddit_info, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error getting subreddit info for r/{subreddit_name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting subreddit info for r/{subreddit_name}: {str(e)}"
        )]

async def post_to_subreddit(args: dict[str, Any]) -> list[types.TextContent]:
    """Create a new post in a subreddit"""
    subreddit_name = args.get("subreddit")
    title = args.get("title")
    content = args.get("content")
    url = args.get("url")
    
    # Check if we have write permissions
    try:
        reddit.user.me()  # This will fail if we're in read-only mode
    except:
        return [types.TextContent(
            type="text",
            text="Error: Cannot create posts. Reddit app must be a 'script' type app for write operations."
        )]
    
    if not content and not url:
        return [types.TextContent(
            type="text",
            text="Error: Either 'content' (for text post) or 'url' (for link post) must be provided."
        )]
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        if url:
            # Create link post
            submission = subreddit.submit(title=title, url=url)
        else:
            # Create text post
            submission = subreddit.submit(title=title, selftext=content)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "post_id": submission.id,
                "post_url": f"https://reddit.com{submission.permalink}",
                "title": submission.title,
                "subreddit": subreddit_name
            }, indent=2)
        )]
    
    except Exception as e:
        logger.error(f"Error creating post in r/{subreddit_name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error creating post in r/{subreddit_name}: {str(e)}"
        )]

async def main():
    """Main entry point"""
    # Initialize Reddit client
    initialize_reddit()
    
    # Run the server using stdio
    async with stdio_server() as streams:
        await app.run(
            streams[0], 
            streams[1], 
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())