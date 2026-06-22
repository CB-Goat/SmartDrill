"""
修改exam_points表的外键：knowledge_point_id -> unit_id
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/smartdrill')

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查unit_id字段是否存在
    result = conn.execute(text("SHOW COLUMNS FROM exam_points LIKE 'unit_id'"))
    if not result.fetchone():
        # 添加unit_id字段
        conn.execute(text("ALTER TABLE exam_points ADD COLUMN unit_id INT AFTER id"))
        conn.commit()
        print("✓ 已添加unit_id字段")
        
        # 从knowledge_point关联到unit
        conn.execute(text("""
            UPDATE exam_points ep
            JOIN knowledge_points kp ON ep.knowledge_point_id = kp.id
            SET ep.unit_id = kp.unit_id
        """))
        conn.commit()
        print("✓ 已填充unit_id数据")
        
        # 设置unit_id为NOT NULL
        conn.execute(text("ALTER TABLE exam_points MODIFY unit_id INT NOT NULL"))
        conn.commit()
        print("✓ unit_id设置为NOT NULL")
        
        # 添加外键约束
        conn.execute(text("""
            ALTER TABLE exam_points 
            ADD CONSTRAINT fk_exam_points_unit 
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
        """))
        conn.commit()
        print("✓ 已添加外键约束")
        
        # 删除旧的外键和字段
        try:
            conn.execute(text("ALTER TABLE exam_points DROP FOREIGN KEY fk_exam_points_knowledge_point"))
            conn.commit()
            print("✓ 已删除旧外键")
        except:
            print("- 旧外键不存在或已删除")
        
        conn.execute(text("ALTER TABLE exam_points DROP COLUMN knowledge_point_id"))
        conn.commit()
        print("✓ 已删除knowledge_point_id字段")
    else:
        print("unit_id字段已存在，跳过迁移")

print("迁移完成！")