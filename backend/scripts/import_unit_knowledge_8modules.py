"""
8大模块知识点导入脚本
从Excel读取单元知识，按 科目/年级/学期/单元序号 匹配数据库中的Unit，
写入 unit_knowledge_json 字段，并同步更新 knowledge_points 表。
"""

import sys
import os
import json
import openpyxl
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.models import Unit, KnowledgePoint, Semester, Subject, Grade, Version

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '人教版全学科单元知识点_8大模块_完整版_20260626.xlsx')


def ensure_column():
    """确保 unit_knowledge_json 列存在"""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM units LIKE 'unit_knowledge_json'"))
            row = result.fetchone()
            if not row:
                conn.execute(text("ALTER TABLE units ADD COLUMN unit_knowledge_json JSON"))
                conn.commit()
                print('✓ 已添加 unit_knowledge_json 字段')
            else:
                print('✓ unit_knowledge_json 字段已存在')
    except Exception as e:
        print(f'检查字段时出错（可能是SQLite）: {e}')
        # SQLite 用另一种方式
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE units ADD COLUMN unit_knowledge_json JSON"))
                conn.commit()
        except Exception as e2:
            print(f'  SQLite 添加字段也失败（可能已存在）: {e2}')


def find_unit(db, subject_name, grade_name, semester_name, unit_number, unit_name):
    """根据科目/年级/学期/单元序号匹配Unit"""
    # 逐级匹配
    version = db.query(Version).filter(Version.name.like('%人教%')).first()
    if not version:
        version = db.query(Version).first()
    if not version:
        return None

    grade = db.query(Grade).filter(
        Grade.version_id == version.id,
        Grade.name == grade_name
    ).first()
    if not grade:
        return None

    subject = db.query(Subject).filter(
        Subject.grade_id == grade.id,
        Subject.name == subject_name
    ).first()
    if not subject:
        return None

    semester = db.query(Semester).filter(
        Semester.subject_id == subject.id,
        Semester.name == semester_name
    ).first()
    if not semester:
        return None

    unit = db.query(Unit).filter(
        Unit.semester_id == semester.id,
        Unit.unit_number == unit_number
    ).first()

    return unit


def parse_excel():
    """解析Excel，返回单元数据列表"""
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active

    units_data = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        subject = row[0]
        grade = row[1]
        semester = row[2]
        unit_num = row[3]
        unit_code = row[4]
        unit_name = row[5]
        unit_topic = row[6]
        unit_overview = row[7]
        knowledge_frame = row[8]
        core_concepts_text = row[9]
        key_knowledge_text = row[10]
        difficult_analysis_text = row[11]
        confuse_distinction_text = row[12]
        typical_example_json = row[13]
        raw_knowledge = row[14]
        json_content = row[15]

        if not subject or not unit_name:
            continue

        # 解析JSON内容（第16列是完整的8大模块JSON）
        knowledge_data = None
        if json_content:
            try:
                knowledge_data = json.loads(str(json_content))
            except Exception as e:
                print(f'  第{row_idx}行JSON解析失败: {e}')

        # 如果JSON内容列解析失败，从各列手动组装
        if not knowledge_data:
            # 解析数组列
            def parse_array(text):
                if not text:
                    return []
                lines = [l.strip() for l in str(text).split('\n') if l.strip()]
                items = []
                for line in lines:
                    # 去掉开头的序号
                    cleaned = line
                    cleaned = __import__('re').sub(r'^\d+[.、．)]\s*', '', cleaned)
                    cleaned = __import__('re').sub(r'^[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]\s*', '', cleaned)
                    if cleaned:
                        items.append(cleaned)
                return items

            typical_example = {}
            if typical_example_json:
                try:
                    typical_example = json.loads(str(typical_example_json))
                except:
                    typical_example = {'stem': str(typical_example_json)[:500]}

            knowledge_data = {
                'unit_topic': str(unit_topic or ''),
                'unit_overview': str(unit_overview or ''),
                'knowledge_frame': str(knowledge_frame or ''),
                'core_concepts': parse_array(core_concepts_text),
                'key_knowledge': parse_array(key_knowledge_text),
                'difficult_analysis': parse_array(difficult_analysis_text),
                'confuse_distinction': parse_array(confuse_distinction_text),
                'typical_example': typical_example
            }

        units_data.append({
            'subject': subject,
            'grade': grade,
            'semester': semester,
            'unit_number': unit_num,
            'unit_name': unit_name,
            'knowledge_data': knowledge_data
        })

    return units_data


def sync_knowledge_points(db, unit_id, knowledge_data):
    """同步更新knowledge_points表，从8大模块中提取知识点"""
    if not knowledge_data:
        return 0, 0

    # 知识点来源：核心概念 + 重点知识 + 难点解析 + 易混辨析
    kp_sources = [
        ('核心概念', knowledge_data.get('core_concepts', [])),
        ('重点知识', knowledge_data.get('key_knowledge', [])),
        ('难点解析', knowledge_data.get('difficult_analysis', [])),
        ('易混辨析', knowledge_data.get('confuse_distinction', [])),
    ]

    # 收集所有知识点标题和内容
    all_points = []
    for category, items in kp_sources:
        for idx, item in enumerate(items):
            title = f'[{category}] {item[:50]}'
            if len(item) > 50:
                title += '...'
            content = item
            all_points.append({'title': title, 'content': content, 'category': category})

    if not all_points:
        return 0, 0

    # 删除该单元原有知识点
    db.query(KnowledgePoint).filter(KnowledgePoint.unit_id == unit_id).delete()

    # 插入新知识点
    count = 0
    for point in all_points:
        kp = KnowledgePoint(
            unit_id=unit_id,
            title=point['title'],
            content=point['content']
        )
        db.add(kp)
        count += 1

    return count, 0  # 新增数，更新数


def main():
    print('=' * 60)
    print('8大模块知识点导入')
    print('=' * 60)

    # 1. 确保字段存在
    print('\n[1/4] 检查数据库字段...')
    ensure_column()

    # 2. 解析Excel
    print('\n[2/4] 解析Excel...')
    units_data = parse_excel()
    print(f'  解析到 {len(units_data)} 个单元')

    db = SessionLocal()

    matched = 0
    not_matched = 0
    total_kp = 0

    try:
        print('\n[3/4] 匹配并写入数据库...')
        for i, ud in enumerate(units_data):
            unit = find_unit(
                db,
                ud['subject'],
                ud['grade'],
                ud['semester'],
                ud['unit_number'],
                ud['unit_name']
            )

            if unit:
                matched += 1
                # 写入 unit_knowledge_json
                unit.unit_knowledge_json = ud['knowledge_data']

                # 同步知识点表
                kp_count, _ = sync_knowledge_points(db, unit.id, ud['knowledge_data'])
                total_kp += kp_count

                if (i + 1) % 50 == 0:
                    db.commit()
                    print(f'  进度: {i+1}/{len(units_data)}, 匹配{matched}, 知识点{total_kp}条')
            else:
                not_matched += 1
                print(f'  ⚠ 未匹配: {ud["subject"]}/{ud["grade"]}/{ud["semester"]}/第{ud["unit_number"]}单元 {ud["unit_name"]}')

        db.commit()

        print(f'\n[4/4] 完成！')
        print(f'  匹配成功: {matched} 个单元')
        print(f'  未匹配: {not_matched} 个单元')
        print(f'  新增知识点: {total_kp} 条')

    except Exception as e:
        db.rollback()
        print(f'\n✗ 导入出错: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print('\n' + '=' * 60)


if __name__ == '__main__':
    main()