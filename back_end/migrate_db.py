"""
数据库迁移脚本 - 添加缺失的列
运行方式: python migrate_db.py
"""

import sqlite3
import os

def migrate_database():
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(production_line)")
    columns = [col[1] for col in cursor.fetchall()]
    
    migrations = []
    
    if 'model_path' not in columns:
        migrations.append("ALTER TABLE production_line ADD COLUMN model_path VARCHAR(255)")
        print("将添加 model_path 列到 production_line 表")
    
    if 'line_code' not in columns:
        migrations.append("ALTER TABLE production_line ADD COLUMN line_code VARCHAR(50)")
        print("将添加 line_code 列到 production_line 表")
    
    if 'data_type' not in columns:
        migrations.append("ALTER TABLE production_line ADD COLUMN data_type VARCHAR(20) DEFAULT 'attribute'")
        print("将添加 data_type 列到 production_line 表")
    
    for sql in migrations:
        try:
            cursor.execute(sql)
            print(f"执行成功: {sql}")
        except Exception as e:
            print(f"执行失败: {sql}, 错误: {e}")
    
    cursor.execute("PRAGMA table_info(control_chart_config)")
    cc_columns = [col[1] for col in cursor.fetchall()]
    
    if not cc_columns:
        print("创建 control_chart_config 表...")
        cursor.execute("""
            CREATE TABLE control_chart_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER NOT NULL,
                chart_type VARCHAR(20) DEFAULT 'U',
                control_limit_type VARCHAR(20) DEFAULT 'dynamic',
                alarm_rules TEXT DEFAULT '[]',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("control_chart_config 表创建成功")
    
    cursor.execute("PRAGMA table_info(measurement_data)")
    md_columns = [col[1] for col in cursor.fetchall()]
    
    if not md_columns:
        print("创建 measurement_data 表...")
        cursor.execute("""
            CREATE TABLE measurement_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER NOT NULL,
                sample_id VARCHAR(100) NOT NULL,
                measurement_values TEXT DEFAULT '[]',
                measurement_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                operator VARCHAR(100),
                equipment VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("measurement_data 表创建成功")
    
    cursor.execute("PRAGMA table_info(attribute_data)")
    ad_columns = [col[1] for col in cursor.fetchall()]
    
    if not ad_columns:
        print("创建 attribute_data 表...")
        cursor.execute("""
            CREATE TABLE attribute_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER NOT NULL,
                sample_id VARCHAR(100) NOT NULL,
                sample_size INTEGER DEFAULT 0,
                defect_count INTEGER DEFAULT 0,
                defect_details TEXT DEFAULT '{}',
                inspection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                inspector VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("attribute_data 表创建成功")
    
    cursor.execute("PRAGMA table_info(sampling_plan)")
    sp_columns = [col[1] for col in cursor.fetchall()]
    
    if not sp_columns:
        print("创建 sampling_plan 表...")
        cursor.execute("""
            CREATE TABLE sampling_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER,
                plan_name VARCHAR(100) NOT NULL,
                batch_size INTEGER NOT NULL,
                aql_value VARCHAR(20) DEFAULT '1.0',
                inspection_level VARCHAR(10) DEFAULT 'II',
                sample_size INTEGER,
                acceptance_number INTEGER,
                rejection_number INTEGER,
                sampling_type VARCHAR(20) DEFAULT 'single',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("sampling_plan 表创建成功")
    
    cursor.execute("PRAGMA table_info(sampling_record)")
    sr_columns = [col[1] for col in cursor.fetchall()]
    
    if not sr_columns:
        print("创建 sampling_record 表...")
        cursor.execute("""
            CREATE TABLE sampling_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER,
                line_id INTEGER,
                batch_id VARCHAR(100) NOT NULL,
                sample_size INTEGER NOT NULL,
                defect_count INTEGER DEFAULT 0,
                judgment VARCHAR(20),
                inspection_status VARCHAR(20) DEFAULT 'normal',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("sampling_record 表创建成功")
    
    conn.commit()
    conn.close()
    
    print("\n数据库迁移完成！")

if __name__ == "__main__":
    migrate_database()
