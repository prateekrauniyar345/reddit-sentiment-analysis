"""
Database Manager for Reddit Sentiment Analysis
Handles data persistence and caching
"""

import sqlite3
import json
import asyncio
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "reddit_analysis.db"):
        """Initialize database manager"""
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create analysis results table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        task_id TEXT PRIMARY KEY,
                        query TEXT NOT NULL,
                        total_posts INTEGER,
                        total_comments INTEGER,
                        analysis_duration REAL,
                        created_at TIMESTAMP,
                        result_data TEXT,
                        analytics_data TEXT
                    )
                """)
                
                # Create posts table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS posts (
                        id TEXT PRIMARY KEY,
                        task_id TEXT,
                        title TEXT,
                        selftext TEXT,
                        author TEXT,
                        subreddit TEXT,
                        score INTEGER,
                        upvote_ratio REAL,
                        num_comments INTEGER,
                        created_utc REAL,
                        url TEXT,
                        overall_sentiment REAL,
                        sentiment_label TEXT,
                        engagement_score REAL,
                        FOREIGN KEY (task_id) REFERENCES analysis_results (task_id)
                    )
                """)
                
                # Create comments table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS comments (
                        id TEXT PRIMARY KEY,
                        post_id TEXT,
                        author TEXT,
                        body TEXT,
                        score INTEGER,
                        created_utc REAL,
                        sentiment_score REAL,
                        sentiment_label TEXT,
                        FOREIGN KEY (post_id) REFERENCES posts (id)
                    )
                """)
                
                # Create indexes for better performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_posts_task_id ON posts(task_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_utc ON posts(created_utc)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_analysis_created_at ON analysis_results(created_at)")
                
                await db.commit()
                
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def save_analysis_result(self, result: Any) -> bool:
        """Save analysis result to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Save main analysis result
                await db.execute("""
                    INSERT OR REPLACE INTO analysis_results 
                    (task_id, query, total_posts, total_comments, analysis_duration, created_at, result_data, analytics_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.task_id,
                    result.query,
                    result.total_posts,
                    result.total_comments,
                    result.analysis_duration,
                    result.created_at,
                    json.dumps(result.dict(), default=str),
                    json.dumps(result.analytics, default=str)
                ))
                
                # Save posts
                for post in result.posts:
                    await db.execute("""
                        INSERT OR REPLACE INTO posts 
                        (id, task_id, title, selftext, author, subreddit, score, upvote_ratio, 
                         num_comments, created_utc, url, overall_sentiment, sentiment_label, engagement_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post.id,
                        result.task_id,
                        post.title,
                        post.selftext,
                        post.author,
                        post.subreddit,
                        post.score,
                        post.upvote_ratio,
                        post.num_comments,
                        post.created_utc,
                        post.url,
                        post.overall_sentiment,
                        post.sentiment_label,
                        post.engagement_score
                    ))
                    
                    # Save comments
                    for comment in post.comments:
                        await db.execute("""
                            INSERT OR REPLACE INTO comments 
                            (id, post_id, author, body, score, created_utc, sentiment_score, sentiment_label)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            comment.id,
                            post.id,
                            comment.author,
                            comment.body,
                            comment.score,
                            comment.created_utc,
                            comment.sentiment_score,
                            comment.sentiment_label
                        ))
                
                await db.commit()
                logger.info(f"Saved analysis result {result.task_id} to database")
                return True
                
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            return False
    
    async def get_analysis_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Get main result
                async with db.execute("""
                    SELECT * FROM analysis_results WHERE task_id = ?
                """, (task_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    result_data = json.loads(row['result_data'])
                    return result_data
                    
        except Exception as e:
            logger.error(f"Error getting analysis result: {e}")
            return None
    
    async def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get analysis history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute("""
                    SELECT task_id, query, total_posts, total_comments, analysis_duration, created_at
                    FROM analysis_results 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    history = []
                    for row in rows:
                        history.append({
                            'task_id': row['task_id'],
                            'query': row['query'],
                            'total_posts': row['total_posts'],
                            'total_comments': row['total_comments'],
                            'analysis_duration': row['analysis_duration'],
                            'created_at': row['created_at']
                        })
                    
                    return history
                    
        except Exception as e:
            logger.error(f"Error getting analysis history: {e}")
            return []
    
    async def delete_analysis_result(self, task_id: str) -> bool:
        """Delete analysis result and related data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete comments first (due to foreign key constraints)
                await db.execute("""
                    DELETE FROM comments 
                    WHERE post_id IN (SELECT id FROM posts WHERE task_id = ?)
                """, (task_id,))
                
                # Delete posts
                await db.execute("DELETE FROM posts WHERE task_id = ?", (task_id,))
                
                # Delete main result
                await db.execute("DELETE FROM analysis_results WHERE task_id = ?", (task_id,))
                
                await db.commit()
                logger.info(f"Deleted analysis result {task_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting analysis result: {e}")
            return False
    
    async def get_sentiment_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get sentiment trends over specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        AVG(overall_sentiment) as avg_sentiment,
                        COUNT(*) as post_count
                    FROM analysis_results ar
                    JOIN posts p ON ar.task_id = p.task_id
                    WHERE ar.created_at >= ?
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """, (cutoff_date,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    trends = []
                    for row in rows:
                        trends.append({
                            'date': row['date'],
                            'avg_sentiment': row['avg_sentiment'],
                            'post_count': row['post_count']
                        })
                    
                    return trends
                    
        except Exception as e:
            logger.error(f"Error getting sentiment trends: {e}")
            return []
    
    async def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search queries"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute("""
                    SELECT 
                        query,
                        COUNT(*) as usage_count,
                        AVG(total_posts) as avg_posts,
                        MAX(created_at) as last_used
                    FROM analysis_results
                    GROUP BY query
                    ORDER BY usage_count DESC
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    queries = []
                    for row in rows:
                        queries.append({
                            'query': row['query'],
                            'usage_count': row['usage_count'],
                            'avg_posts': row['avg_posts'],
                            'last_used': row['last_used']
                        })
                    
                    return queries
                    
        except Exception as e:
            logger.error(f"Error getting popular queries: {e}")
            return []
    
    async def cleanup_old_results(self, days: int = 30) -> int:
        """Clean up analysis results older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Get task IDs to delete
                async with db.execute("""
                    SELECT task_id FROM analysis_results WHERE created_at < ?
                """, (cutoff_date,)) as cursor:
                    task_ids = [row[0] for row in await cursor.fetchall()]
                
                if not task_ids:
                    return 0
                
                # Delete related data
                placeholders = ','.join(['?' for _ in task_ids])
                
                await db.execute(f"""
                    DELETE FROM comments 
                    WHERE post_id IN (
                        SELECT id FROM posts WHERE task_id IN ({placeholders})
                    )
                """, task_ids)
                
                await db.execute(f"""
                    DELETE FROM posts WHERE task_id IN ({placeholders})
                """, task_ids)
                
                await db.execute(f"""
                    DELETE FROM analysis_results WHERE task_id IN ({placeholders})
                """, task_ids)
                
                await db.commit()
                
                logger.info(f"Cleaned up {len(task_ids)} old analysis results")
                return len(task_ids)
                
        except Exception as e:
            logger.error(f"Error cleaning up old results: {e}")
            return 0
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                stats = {}
                
                # Count records in each table
                for table in ['analysis_results', 'posts', 'comments']:
                    async with db.execute(f"SELECT COUNT(*) as count FROM {table}") as cursor:
                        row = await cursor.fetchone()
                        stats[f'{table}_count'] = row['count']
                
                # Get database size
                async with db.execute("PRAGMA page_count") as cursor:
                    page_count = (await cursor.fetchone())[0]
                
                async with db.execute("PRAGMA page_size") as cursor:
                    page_size = (await cursor.fetchone())[0]
                
                stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    async def close(self):
        """Close database connections"""
        # Note: aiosqlite connections are context-managed, so no explicit close needed
        logger.info("Database connections closed")