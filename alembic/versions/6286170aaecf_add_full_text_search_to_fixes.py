"""Add full-text search to fixes

Revision ID: 6286170aaecf
Revises: def456_fulltext
Create Date: 2025-08-15 22:41:18.804342

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

# revision identifiers, used by Alembic.
revision = '6286170aaecf'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Populate existing records with search vectors
    op.execute("""
        UPDATE fixes 
        SET document = to_tsvector('english', 
            COALESCE(title, '') || ' ' || 
            COALESCE(problem, '') || ' ' || 
            COALESCE(solution, '')
        )
        WHERE document IS NULL
    """)

    # Create trigger function to automatically update document
    op.execute("""
        CREATE OR REPLACE FUNCTION update_fixes_document()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.document := to_tsvector('english', 
                COALESCE(NEW.title, '') || ' ' || 
                COALESCE(NEW.problem, '') || ' ' || 
                COALESCE(NEW.solution, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger that calls the function on INSERT and UPDATE
    op.execute("""
        CREATE TRIGGER update_fixes_document_trigger
        BEFORE INSERT OR UPDATE OF title, problem, solution
        ON fixes
        FOR EACH ROW
        EXECUTE FUNCTION update_fixes_document();
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_fixes_document_trigger ON fixes")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_fixes_document()")

    # Drop index
    op.drop_index('idx_fixes_document', table_name='fixes')

    # Drop column
    op.drop_column('fixes', 'document')