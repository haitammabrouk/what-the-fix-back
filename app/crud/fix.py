from typing import List, Any, Coroutine, Optional

from sqlalchemy.orm import Session

from app.schemas.fix import FixCreate, FixResponse
from app.models.fix import Fix
from app.models.tag import Tag
from app.services.llm import llm_service

import logging

logger = logging.getLogger(__name__)


class FixCrud:
    async def create(self, db: Session, fix: FixCreate) -> Optional[FixResponse]:
        """Create a fix with AI-generated title and tags using GPT-4o Model"""
        try:
            logger.info("🧠 Generating title and tags with GitHub LLM...")

            # Step 1: Generate title and tags using GitHub LLM
            ai_result = await llm_service.generate_title_and_tags(
                problem=fix.problem,
                solution=fix.solution
            )

            logger.info(f"AI generated - Title: {ai_result['title']}")
            logger.info(f"AI generated - Tags: {ai_result['tags']}")

            # Step 2: Create the fix with generated title
            db_fix = Fix(
                title=ai_result["title"],
                problem=fix.problem,
                solution=fix.solution,
                user_id=fix.user_id
            )

            db.add(db_fix)
            db.flush()  # Get the ID without committing yet

            # Step 3: Create/get tags and associate them
            tag_names = []
            for tag_name in ai_result["tags"]:
                # Get existing tag or create new one
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                    logger.info(f"Created new tag: {tag_name}")
                else:
                    logger.info(f"Using existing tag: {tag_name}")

                # Associate tag with fix
                db_fix.tags.append(tag)
                tag_names.append(tag_name)

            # Step 4: Commit everything
            db.commit()
            db.refresh(db_fix)

            logger.info(f"Fix created successfully: ID {db_fix.id}")
            logger.info(f"Tags: {tag_names}")

            # Step 5: Return FixResponse format
            return FixResponse(
                title=ai_result["title"],
                problem=fix.problem,
                solution=fix.solution,
                tags=tag_names
            )

        except Exception as e:
            logger.error(f"Error while creating the fix: {e}")
            db.rollback()

    def get_all(self, db: Session) -> List[FixResponse]:
        fixes = db.query(Fix).all()
        fix_responses = []
        for fix in fixes:
            tag_names = [tag.name for tag in fix.tags]
            fix_responses.append(
                FixResponse(
                    title=fix.title,
                    problem=fix.problem,
                    solution=fix.solution,
                    tags=tag_names)
                )
        return fix_responses

fix_crud = FixCrud()