"""
GitLab API Client
Handles all interactions with GitLab API
"""

import gitlab
import logging
from typing import Dict, List, Any, Optional

from backend.config import settings
from backend.models import AnalysisResult

logger = logging.getLogger(__name__)


class GitLabClient:
    """Client for interacting with GitLab API"""
    
    def __init__(self):
        try:
            self.gl = gitlab.Gitlab(
                url=settings.GITLAB_URL,
                private_token=settings.GITLAB_TOKEN
            )
            self.gl.auth()
            logger.info(f"✅ GitLab client connected to {settings.GITLAB_URL}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to GitLab: {str(e)}")
            raise
    
    def get_project(self, project_id: int):
        """Get GitLab project by ID"""
        try:
            return self.gl.projects.get(project_id)
        except Exception as e:
            logger.error(f"❌ Failed to get project {project_id}: {str(e)}")
            raise
    
    def get_merge_request(self, project_id: int, mr_iid: int):
        """Get Merge Request details"""
        try:
            project = self.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            logger.info(f"📋 Got MR #{mr_iid}: {mr.title}")
            return mr
        except Exception as e:
            logger.error(f"❌ Failed to get MR {mr_iid}: {str(e)}")
            raise
    
    def get_mr_changes(self, project_id: int, mr_iid: int) -> List[Dict]:
        """Get changes (diff) from Merge Request"""
        try:
            project = self.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Debug: log MR state
            logger.info(f"🔍 MR State: {mr.state}, Has conflicts: {mr.has_conflicts}, Mergeable: {getattr(mr, 'merge_status', 'unknown')}")
            
            # Get changes with retries
            changes = mr.changes()
            
            # Debug: log what we got
            logger.info(f"📦 Changes keys: {list(changes.keys())}")
            logger.info(f"📦 Changes type: {type(changes)}")
            
            # Extract changes
            file_changes = changes.get('changes', [])
            
            # If no changes, try diff
            if not file_changes:
                logger.warning("⚠️ No changes in mr.changes(), trying diffs...")
                try:
                    diffs = mr.diffs.list()
                    if diffs:
                        logger.info(f"📝 Found {len(diffs)} diffs")
                        file_changes = [diff.attributes for diff in diffs]
                except Exception as diff_err:
                    logger.warning(f"⚠️ Could not get diffs: {diff_err}")
            
            logger.info(f"📝 Got {len(file_changes)} file changes")
            
            return file_changes
            
        except Exception as e:
            logger.error(f"❌ Failed to get MR changes: {str(e)}")
            raise
    
    def _format_review_summary(self, analysis: Dict[str, Any]) -> str:
        """Format analysis result into markdown summary"""
        
        score = analysis['score']
        recommendation = analysis['recommendation']
        critical = analysis['critical_count']
        medium = analysis['medium_count']
        low = analysis['low_count']
        summary = analysis['summary']
        
        # Emoji based on score
        if score >= 8.0:
            emoji = "✅"
        elif score >= 6.0:
            emoji = "⚠️"
        else:
            emoji = "🔴"
        
        # Recommendation text
        rec_text = {
            "merge": "✅ Готово к слиянию",
            "needs_fixes": "⚠️ Требуются исправления",
            "reject": "🔴 Требуется переработка"
        }.get(recommendation, "🔍 Требуется проверка")
        
        markdown = f"""## 🤖 AI Code Review

{emoji} **Оценка качества кода: {score}/10**

### Рекомендация: {rec_text}

### 📊 Найдено проблем:
- 🔴 Критические: **{critical}**
- 🟡 Средние: **{medium}**
- 🟢 Низкие: **{low}**

### 📝 Резюме:
{summary}

### ⏱️ Экономия времени:
Автоматический анализ сэкономил **~{analysis.get('estimated_time_saved', 90)} минут** времени сеньора.

---
*Это автоматическая проверка от AI Code Review Assistant*
"""
        return markdown
    
    def _format_issue_comment(self, issue: Dict[str, Any]) -> str:
        """Format single issue into markdown comment"""
        
        severity_emoji = {
            "critical": "🔴",
            "medium": "🟡",
            "low": "🟢",
            "info": "💡"
        }
        
        type_emoji = {
            "security": "🔐",
            "performance": "⚡",
            "bug": "🐛",
            "code_style": "📖",
            "best_practice": "✨",
            "architecture": "🏗️"
        }
        
        severity = issue.get('severity', 'info')
        issue_type = issue.get('issue_type', 'best_practice')
        
        emoji = severity_emoji.get(severity, "💡")
        type_icon = type_emoji.get(issue_type, "📝")
        
        severity_text = {
            "critical": "КРИТИЧЕСКАЯ ПРОБЛЕМА",
            "medium": "Средняя проблема",
            "low": "Низкая проблема",
            "info": "Совет"
        }.get(severity, "Замечание")
        
        comment = f"""{emoji} **{severity_text}** {type_icon}

**Проблема:**
{issue.get('description', 'Не указано')}

**Рекомендация:**
{issue.get('suggestion', 'Не указано')}
"""
        
        if issue.get('code_snippet'):
            comment += f"""
**Проблемный код:**
```
{issue['code_snippet']}
```
"""
        
        comment += f"\n*Категория: {issue_type}*"
        
        return comment
    
    def post_review_comments(
        self,
        project_id: int,
        mr_iid: int,
        analysis_result: Dict[str, Any]
    ):
        """Post review comments to GitLab MR"""
        try:
            project = self.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Post summary comment
            summary_comment = self._format_review_summary(analysis_result)
            mr.notes.create({'body': summary_comment})
            logger.info("✅ Posted summary comment")
            
            # Post individual issue comments
            issues_posted = 0
            for issue in analysis_result.get('issues', []):
                # Only post critical and medium issues as comments
                # (to avoid spam)
                if issue.get('severity') in ['critical', 'medium']:
                    comment_text = self._format_issue_comment(issue)
                    
                    # Try to post as line comment if line number exists
                    if issue.get('line'):
                        try:
                            # Create discussion on specific line
                            mr.discussions.create({
                                'body': comment_text,
                                'position': {
                                    'base_sha': mr.diff_refs['base_sha'],
                                    'start_sha': mr.diff_refs['start_sha'],
                                    'head_sha': mr.diff_refs['head_sha'],
                                    'position_type': 'text',
                                    'new_path': issue.get('file_path'),
                                    'new_line': issue.get('line')
                                }
                            })
                        except Exception as e:
                            # If line comment fails, post as general comment
                            logger.warning(f"⚠️ Failed to post line comment: {str(e)}")
                            mr.notes.create({'body': f"**{issue.get('file_path')}:{issue.get('line')}**\n\n{comment_text}"})
                    else:
                        # Post as general comment
                        mr.notes.create({'body': f"**{issue.get('file_path')}**\n\n{comment_text}"})
                    
                    issues_posted += 1
            
            logger.info(f"✅ Posted {issues_posted} issue comments")
            
        except Exception as e:
            logger.error(f"❌ Failed to post comments: {str(e)}")
            raise
    
    def update_mr_labels(self, project_id: int, mr_iid: int, score: float):
        """Update MR labels based on analysis score"""
        try:
            project = self.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Remove old AI labels
            current_labels = mr.labels
            ai_labels = ['ai-approved', 'ai-needs-review', 'ai-needs-fixes']
            new_labels = [l for l in current_labels if l not in ai_labels]
            
            # Add new label based on score
            if score >= 8.0:
                new_labels.append('ai-approved')
            elif score >= 6.0:
                new_labels.append('ai-needs-review')
            else:
                new_labels.append('ai-needs-fixes')
            
            # Update labels
            mr.labels = new_labels
            mr.save()
            
            logger.info(f"🏷️ Updated labels: {new_labels}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to update labels: {str(e)}")
