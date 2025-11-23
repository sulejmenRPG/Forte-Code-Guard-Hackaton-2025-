"""
Reaction Poller - Периодически проверяет reactions на AI комментарии
Используется вместо webhooks т.к. GitLab не отправляет события для emoji
"""

import asyncio
import logging
from typing import List, Dict, Set
from datetime import datetime, timedelta

from backend.gitlab_client import GitLabClient
from backend.feedback import learning_system, Feedback
from backend.database import get_recent_reviews

logger = logging.getLogger(__name__)


class ReactionPoller:
    """Периодически проверяет reactions на AI комментарии"""
    
    def __init__(self, gitlab_client: GitLabClient, check_interval: int = 60):
        self.gitlab_client = gitlab_client
        self.check_interval = check_interval  # seconds
        self.processed_reactions: Set[str] = set()  # comment_id:reaction_type
        self.running = False
        
    async def start(self):
        """Запустить polling в фоне"""
        self.running = True
        logger.info(f"🔄 Reaction poller started (interval: {self.check_interval}s)")
        
        while self.running:
            try:
                await self.check_recent_comments()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in reaction poller: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Остановить polling"""
        self.running = False
        logger.info("🛑 Reaction poller stopped")
    
    async def check_recent_comments(self):
        """Проверить reactions на недавних AI комментариях"""
        try:
            # Получить недавние reviews из БД (за последние 24 часа)
            recent_reviews = get_recent_reviews(limit=50)
            
            if not recent_reviews:
                logger.debug("No recent reviews to check")
                return
            
            logger.info(f"🔍 Checking reactions on {len(recent_reviews)} recent reviews")
            
            for review in recent_reviews:
                try:
                    await self.check_review_comments(
                        project_id=review.get('project_id'),
                        mr_iid=review.get('mr_id')
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Error checking review {review.get('mr_id')}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error in check_recent_comments: {str(e)}")
    
    async def check_review_comments(self, project_id: int, mr_iid: int):
        """Проверить reactions на комментариях в конкретном MR"""
        try:
            # Получить MR
            project = self.gitlab_client.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Получить все комментарии
            notes = mr.notes.list(get_all=True)
            
            # Фильтровать только AI комментарии
            ai_notes = [
                note for note in notes 
                if "🤖" in note.body or "AI Review" in note.body or "AI Code Review" in note.body
            ]
            
            if not ai_notes:
                return
            
            logger.debug(f"📝 Found {len(ai_notes)} AI comments in MR #{mr_iid}")
            
            # Проверить reactions на каждом AI комментарии
            for note in ai_notes:
                await self.process_note_reactions(
                    project_id=project_id,
                    mr_iid=mr_iid,
                    note_id=note.id,
                    note_body=note.body,
                    author_name=mr.author.get('name', 'Unknown')
                )
                
        except Exception as e:
            logger.error(f"❌ Error checking MR {mr_iid}: {str(e)}")
    
    async def process_note_reactions(
        self, 
        project_id: int, 
        mr_iid: int, 
        note_id: int, 
        note_body: str,
        author_name: str
    ):
        """Обработать reactions на конкретном комментарии"""
        try:
            # Получить reactions
            reactions = self.gitlab_client.get_note_reactions(project_id, mr_iid, note_id)
            
            if not reactions:
                return
            
            # Проверить thumbsdown
            thumbsdown_key = f"{note_id}:thumbsdown"
            if 'thumbsdown' in reactions or '-1' in reactions:
                if thumbsdown_key not in self.processed_reactions:
                    # Создать negative feedback
                    feedback = Feedback(
                        comment_id=str(note_id),
                        mr_id=mr_iid,
                        project_id=project_id,
                        feedback_type='negative',
                        reason="Senior marked AI comment as incorrect (via polling)",
                        senior_name=author_name,
                        ai_comment=note_body[:500]
                    )
                    
                    learning_system.add_feedback(feedback)
                    self.processed_reactions.add(thumbsdown_key)
                    logger.info(f"❌ Negative feedback recorded for note {note_id}")
            
            # Проверить thumbsup
            thumbsup_key = f"{note_id}:thumbsup"
            if 'thumbsup' in reactions or '+1' in reactions:
                if thumbsup_key not in self.processed_reactions:
                    # Создать positive feedback
                    feedback = Feedback(
                        comment_id=str(note_id),
                        mr_id=mr_iid,
                        project_id=project_id,
                        feedback_type='positive',
                        reason="Senior approved AI comment (via polling)",
                        senior_name=author_name,
                        ai_comment=note_body[:500]
                    )
                    
                    learning_system.add_feedback(feedback)
                    self.processed_reactions.add(thumbsup_key)
                    logger.info(f"✅ Positive feedback recorded for note {note_id}")
                    
        except Exception as e:
            logger.error(f"❌ Error processing reactions for note {note_id}: {str(e)}")


# Global instance
reaction_poller: ReactionPoller = None


def start_reaction_poller(gitlab_client: GitLabClient, check_interval: int = 60):
    """Запустить reaction poller в фоне"""
    global reaction_poller
    
    if reaction_poller is None:
        reaction_poller = ReactionPoller(gitlab_client, check_interval)
    
    # Запустить в background task
    asyncio.create_task(reaction_poller.start())
    logger.info("🔄 Reaction poller background task started")


def stop_reaction_poller():
    """Остановить reaction poller"""
    global reaction_poller
    
    if reaction_poller:
        reaction_poller.stop()
