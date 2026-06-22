"""
添加unit_number字段到units表
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/smartdrill')

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查字段是否存在
    result = conn.execute(text("SHOW COLUMNS FROM units LIKE 'unit_number'"))
    if not result.fetchone():
        # 添加unit_number字段
        conn.execute(text("ALTER TABLE units ADD COLUMN unit_number VARCHAR(20) NOT NULL DEFAULT '' AFTER semester_id"))
        conn.commit()
        print("✓ 已添加unit_number字段")
        
        # 从name中提取unit_number
        conn.execute(text("""
            UPDATE units 
            SET unit_number = TRIM(SUBSTRING_INDEX(name, ' ', 1))
            WHERE name LIKE '% %'
        """))
        conn.commit()
        print("✓ 已从name中提取unit_number")
        
        # 更新name，去掉unit_number部分
        conn.execute(text("""
            UPDATE units 
            SET name = TRIM(SUBSTRING(name, LENGTH(unit_number) + 2))
            WHERE name LIKE CONCAT(unit_number, ' %')
        """))
        conn.commit()
        print("✓ 已更新name字段")
    else:
        print("unit_number字段已存在")

print("迁移完成！")