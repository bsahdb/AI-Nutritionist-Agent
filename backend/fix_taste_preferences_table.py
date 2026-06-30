from sqlalchemy import text
from core.database import engine


REQUIRED_COLUMNS = {
    "preference_name": "VARCHAR(100) DEFAULT '默认口味偏好'",
    "is_default": "BOOLEAN DEFAULT TRUE",
    "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
}


def column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() > 0


def main():
    table_name = "taste_preferences"

    with engine.begin() as conn:
        for column_name, column_def in REQUIRED_COLUMNS.items():
            if not column_exists(conn, table_name, column_name):
                print(f"添加字段：{column_name}")
                conn.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
                )
            else:
                print(f"字段已存在：{column_name}")

    print("taste_preferences 表结构修复完成")


if __name__ == "__main__":
    main()