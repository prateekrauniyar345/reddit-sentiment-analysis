"""
Reddit Service for async data fetching
Handles large-scale Reddit data collection with rate limiting
"""

import praw
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from concurrent.futures import ThreadPoolExecutor
import time

load_dotenv()
logger = logging.getLogger(__name__)

class RedditService:
    def __init__(self):
        """Initialize Reddit service with credentials"""
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
        self.max_workers = 20  # Increased for better concurrency
        self.rate_limit_delay = 0.1  # Delay between requests
        
    async def fetch_posts_async(
        self,
        query: str,
        limit: int = 100,
        subreddits: Optional[List[str]] = None,
        time_filter: str = "week",
        sort_type: str = "relevance",
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch Reddit posts asynchronously with improved error handling
        """
        logger.info(f"Starting async fetch for query: {query}, limit: {limit}")
        
        posts_data = []
        
        try:
            # If specific subreddits are provided, search in those
            if subreddits:
                tasks = []
                for subreddit in subreddits:
                    task = self._fetch_from_subreddit(
                        subreddit, query, limit // len(subreddits), time_filter, sort_type
                    )
                    tasks.append(task)
                
                # Execute subreddit searches concurrently
                subreddit_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in subreddit_results:
                    if isinstance(result, list):
                        posts_data.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Subreddit fetch error: {result}")
            else:
                # Search across all subreddits
                posts_data = await self._fetch_from_all_subreddits(
                    query, limit, time_filter, sort_type, progress_callback
                )
                
        except Exception as e:
            logger.error(f"Error in fetch_posts_async: {e}")
            raise
            
        logger.info(f"Fetched {len(posts_data)} posts successfully")
        return posts_data
    
    async def _fetch_from_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int,
        time_filter: str,
        sort_type: str
    ) -> List[Dict[str, Any]]:
        """Fetch posts from a specific subreddit"""
        posts_data = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Choose search method based on sort_type
            if sort_type == "hot":
                search_results = subreddit.hot(limit=limit)
            elif sort_type == "top":
                search_results = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_type == "new":
                search_results = subreddit.new(limit=limit)
            else:  # relevance (search)
                search_results = subreddit.search(query, time_filter=time_filter, limit=limit)
            
            # Process posts with threading for better performance
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for post in search_results:
                    future = executor.submit(self._process_single_post, post)
                    futures.append(future)
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)
                
                # Collect results
                for future in futures:
                    try:
                        post_data = future.result(timeout=30)  # 30 second timeout
                        if post_data:
                            posts_data.append(post_data)
                    except Exception as e:
                        logger.error(f"Error processing post: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error fetching from subreddit {subreddit_name}: {e}")
            
        return posts_data
    
    async def _fetch_from_all_subreddits(
        self,
        query: str,
        limit: int,
        time_filter: str,
        sort_type: str,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """Fetch posts from all subreddits"""
        posts_data = []
        
        try:
            # Search across all subreddits
            search_results = self.reddit.subreddit("all").search(
                query, 
                time_filter=time_filter, 
                limit=limit,
                sort=sort_type
            )
            
            # Process posts in batches for better memory management
            batch_size = 50
            posts_batch = []
            processed_count = 0
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for post in search_results:
                    posts_batch.append(post)
                    
                    if len(posts_batch) >= batch_size:
                        # Process batch
                        batch_data = await self._process_post_batch(executor, posts_batch)
                        posts_data.extend(batch_data)
                        
                        processed_count += len(posts_batch)
                        posts_batch = []
                        
                        # Update progress
                        if progress_callback:
                            progress = min(int((processed_count / limit) * 100), 100)
                            progress_callback(progress)
                        
                        # Rate limiting between batches
                        await asyncio.sleep(0.5)
                
                # Process remaining posts
                if posts_batch:
                    batch_data = await self._process_post_batch(executor, posts_batch)
                    posts_data.extend(batch_data)
                    
        except Exception as e:
            logger.error(f"Error in _fetch_from_all_subreddits: {e}")
            
        return posts_data
    
    async def _process_post_batch(self, executor: ThreadPoolExecutor, posts_batch: List) -> List[Dict[str, Any]]:
        """Process a batch of posts concurrently"""
        futures = []
        
        for post in posts_batch:
            future = executor.submit(self._process_single_post, post)
            futures.append(future)
        
        batch_data = []
        for future in futures:
            try:
                post_data = future.result(timeout=30)
                if post_data:
                    batch_data.append(post_data)
            except Exception as e:
                logger.error(f"Error processing post in batch: {e}")
                continue
                
        return batch_data
    
    def _process_single_post(self, post) -> Optional[Dict[str, Any]]:
        """Process a single Reddit post and extract all relevant data"""
        try:
            # Extract basic post information
            post_data = {
                'id': post.id,
                'title': post.title,
                'selftext': post.selftext or '',
                'author': post.author.name if post.author else 'Unknown',
                'subreddit': str(post.subreddit),
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'num_comments': post.num_comments,
                'created_utc': post.created_utc,
                'url': post.url,
                'is_video': post.is_video,
                'over_18': post.over_18,
                'permalink': f"https://reddit.com{post.permalink}",
                'comments': []
            }
            
            # Extract comments with improved handling
            post.comment_sort = "top"  # Sort by top comments
            post.comments.replace_more(limit=5)  # Get more comments
            
            all_comments = post.comments.list()
            
            # Filter and process comments
            valid_comments = [
                comment for comment in all_comments 
                if hasattr(comment, 'body') and 
                comment.body not in ['[removed]', '[deleted]'] and
                len(comment.body.strip()) > 10  # Filter out very short comments
            ]
            
            # Take top comments based on score and recency
            top_comments = sorted(valid_comments, key=lambda x: x.score, reverse=True)[:20]
            
            for comment in top_comments:
                try:
                    comment_data = {
                        'id': comment.id,
                        'author': comment.author.name if comment.author else 'Unknown',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'permalink': f"https://reddit.com{comment.permalink}"
                    }
                    post_data['comments'].append(comment_data)
                except Exception as e:
                    logger.warning(f"Error processing comment: {e}")
                    continue
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error processing post {post.id if hasattr(post, 'id') else 'unknown'}: {e}")
            return None
    
    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """Get information about a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            return {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'created_utc': subreddit.created_utc,
                'over_18': subreddit.over18
            }
        except Exception as e:
            logger.error(f"Error getting subreddit info for {subreddit_name}: {e}")
            return {}
    
    async def search_trending_topics(self, limit: int = 50) -> List[str]:
        """Get trending topics from popular subreddits"""
        try:
            trending_posts = self.reddit.subreddit("popular").hot(limit=limit)
            topics = []
            
            for post in trending_posts:
                # Extract keywords from title
                words = post.title.lower().split()
                # Filter out common words and get meaningful terms
                keywords = [word for word in words if len(word) > 3 and word.isalpha()]
                topics.extend(keywords[:3])  # Take first 3 keywords from each title
            
            # Return most common topics
            from collections import Counter
            return [topic for topic, count in Counter(topics).most_common(20)]
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []