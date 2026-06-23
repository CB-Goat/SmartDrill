from sqlalchemy import text
from app.database import engine

def upgrade():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN child_grade_id INTEGER"))
            print("Added child_grade_id column")
        except Exception as e:
            print(f"child_grade_id column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN child_grade_set_at DATETIME"))
            print("Added child_grade_set_at column")
        except Exception as e:
            print(f"child_grade_set_at column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE users ADD CONSTRAINT fk_child_grade FOREIGN KEY (child_grade_id) REFERENCES grades(id)"))
            print("Added foreign key constraint")
        except Exception as e:
            print(f"Foreign key may already exist: {e}")
        
        conn.commit()
        print("Migration completed successfully")

if __name__ == "__main__":
    upgrade()