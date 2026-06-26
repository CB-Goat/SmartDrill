import sys
sys.path.insert(0, '/workspace/backend')

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import Difficulty, Question

STANDARD_DIFFICULTIES = ["简单", "中等", "困难"]

DIFFICULTY_MAPPING = {
    "easy": "简单",
    "normal": "中等",
    "hard": "困难",
    "普通": "简单",
    "一般": "简单",
    "基础": "简单",
    "较易": "简单",
    "困难": "困难",
    "较难": "困难",
    "复杂": "困难",
    "中等": "中等",
    "适中": "中等",
}

def clean_difficulties():
    db: Session = SessionLocal()
    
    try:
        print("=== 当前难度数据 ===")
        difficulties = db.query(Difficulty).all()
        for d in difficulties:
            print(f"ID: {d.id}, 名称: {repr(d.name)}")
        
        print(f"\n共 {len(difficulties)} 条记录")
        
        print("\n=== 清理计划 ===")
        
        standard_diffs = {}
        for name in STANDARD_DIFFICULTIES:
            d = db.query(Difficulty).filter(Difficulty.name == name).first()
            if not d:
                d = Difficulty(name=name)
                db.add(d)
                db.commit()
            standard_diffs[name] = d.id
            print(f"保留标准难度: {name} (ID: {d.id})")
        
        print("\n=== 迁移题目难度 ===")
        migrated_count = 0
        deleted_count = 0
        
        for d in difficulties:
            if d.name in STANDARD_DIFFICULTIES:
                continue
            
            mapped_name = DIFFICULTY_MAPPING.get(d.name)
            if mapped_name and mapped_name in standard_diffs:
                new_diff_id = standard_diffs[mapped_name]
                
                questions = db.query(Question).filter(Question.difficulty_id == d.id).all()
                for q in questions:
                    q.difficulty_id = new_diff_id
                db.commit()
                
                print(f"迁移难度 '{d.name}' (ID: {d.id}) 的 {len(questions)} 道题 -> '{mapped_name}' (ID: {new_diff_id})")
                migrated_count += len(questions)
                
                db.delete(d)
                db.commit()
                deleted_count += 1
            else:
                print(f"未知难度 '{d.name}' (ID: {d.id}), 需要手动处理")
        
        print(f"\n=== 清理完成 ===")
        print(f"迁移题目: {migrated_count} 道")
        print(f"删除难度: {deleted_count} 个")
        
        print("\n=== 清理后难度数据 ===")
        difficulties = db.query(Difficulty).all()
        for d in difficulties:
            q_count = db.query(Question).filter(Question.difficulty_id == d.id).count()
            print(f"ID: {d.id}, 名称: {repr(d.name)}, 题目数: {q_count}")
        
    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_difficulties()
