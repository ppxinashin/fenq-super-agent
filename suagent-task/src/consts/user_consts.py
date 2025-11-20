"""
用户相关常量
"""

class UserConsts:
    """用户相关常量集合"""
    
    # 用户名长度限制
    USERNAME_MAX_LENGTH = 50  # 数据库字段长度
    USERNAME_DISPLAY_MAX_LENGTH = 20  # 前端显示/输入限制
    USERNAME_MIN_LENGTH = 3
    USERNAME_PATTERN = r"^[A-Za-z0-9_]{" + str(USERNAME_MIN_LENGTH) + "," + str(USERNAME_DISPLAY_MAX_LENGTH) + "}$"
    USERNAME_RULE_DESC = f"仅支持大小写字母、数字以及下划线，长度需在{USERNAME_MIN_LENGTH}-{USERNAME_DISPLAY_MAX_LENGTH}字符之间"
    
    # 密码长度限制
    PASSWORD_MAX_LENGTH = 32
    PASSWORD_MIN_LENGTH = 8
    
    # 枚举
    USER_ROLE_ADMIN = "admin"
    USER_ROLE_USER = "user"