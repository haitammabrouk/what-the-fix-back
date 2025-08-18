"""create the migration script for trigerring the computation of newly added fixes or newly updated rows to tsvector

Revision ID: ac0bb7032806
Revises: 33c5d1702b34
Create Date: 2025-08-18 21:25:37.060116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac0bb7032806'
down_revision = '33c5d1702b34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old trigger and function
    op.execute("DROP TRIGGER IF EXISTS update_fixes_document_trigger ON fixes;")
    op.execute("DROP FUNCTION IF EXISTS update_fixes_document_tsvector();")

    # Create enhanced trigger function that includes tags
    op.execute("""
        CREATE OR REPLACE FUNCTION update_fixes_document_tsvector()
        RETURNS TRIGGER AS $$
        DECLARE
            tag_text TEXT;
        BEGIN
            -- Get all tag names for this fix, concatenated with spaces
            SELECT COALESCE(string_agg(t.name, ' '), '') INTO tag_text
            FROM tags t
            INNER JOIN fix_tag ft ON t.id = ft.tag_id
            WHERE ft.fix_id = NEW.id;

            -- Combine all fields with different weights
            -- A = highest weight (title)
            -- B = high weight (problem) 
            -- C = medium weight (solution)
            -- D = lower weight (tags)
            NEW.document := 
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.problem, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.solution, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(tag_text, '')), 'A');

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on fixes table
    op.execute("""
        CREATE TRIGGER update_fixes_document_trigger
        BEFORE INSERT OR UPDATE OF title, problem, solution
        ON fixes
        FOR EACH ROW
        EXECUTE FUNCTION update_fixes_document_tsvector();
    """)

    # Create trigger on fix_tag junction table to update fixes when tags change
    op.execute("""
        CREATE OR REPLACE FUNCTION update_fix_document_on_tag_change()
        RETURNS TRIGGER AS $$
        DECLARE
            fix_id_to_update INTEGER;
        BEGIN
            -- Determine which fix_id to update based on operation
            IF TG_OP = 'DELETE' THEN
                fix_id_to_update := OLD.fix_id;
            ELSE
                fix_id_to_update := NEW.fix_id;
            END IF;

            -- Update the fix's document column
            UPDATE fixes 
            SET updated_at = NOW()  -- This will trigger the main document update
            WHERE id = fix_id_to_update;

            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on fix_tag table for tag associations
    op.execute("""
        CREATE TRIGGER update_fix_document_on_tag_change_trigger
        AFTER INSERT OR DELETE
        ON fix_tag
        FOR EACH ROW
        EXECUTE FUNCTION update_fix_document_on_tag_change();
    """)

    # Update existing records to include tags
    op.execute("""
        UPDATE fixes 
        SET document = (
            setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(problem, '')), 'B') ||
            setweight(to_tsvector('english', COALESCE(solution, '')), 'C') ||
            setweight(to_tsvector('english', COALESCE(
                (SELECT string_agg(t.name, ' ') 
                 FROM tags t 
                 INNER JOIN fix_tag ft ON t.id = ft.tag_id 
                 WHERE ft.fix_id = fixes.id), '')), 'D')
        );
    """)


def downgrade() -> None:
    # Drop the new triggers and functions
    op.execute("DROP TRIGGER IF EXISTS update_fix_document_on_tag_change_trigger ON fix_tag;")
    op.execute("DROP FUNCTION IF EXISTS update_fix_document_on_tag_change();")
    op.execute("DROP TRIGGER IF EXISTS update_fixes_document_trigger ON fixes;")
    op.execute("DROP FUNCTION IF EXISTS update_fixes_document_tsvector();")

    # Restore the original simple trigger (without tags)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_fixes_document_tsvector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.document := 
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.problem, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.solution, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER update_fixes_document_trigger
        BEFORE INSERT OR UPDATE OF title, problem, solution
        ON fixes
        FOR EACH ROW
        EXECUTE FUNCTION update_fixes_document_tsvector();
    """)