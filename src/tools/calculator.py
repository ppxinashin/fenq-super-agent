"""
计算器工具 - 安全的数学表达式求值
"""

import ast
import operator
from typing import Union
from langchain_core.tools import tool

from src.utils import get_logger

logger = get_logger(__name__)


# 支持的运算符
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> Union[int, float]:
    """
    安全地评估数学表达式（仅支持数字和基本运算符）
    
    Args:
        node: AST 节点
    
    Returns:
        计算结果
    """
    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"不支持的常量类型: {type(node.value)}")
    
    elif isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        op_type = type(node.op)
        
        if op_type not in OPERATORS:
            raise ValueError(f"不支持的运算符: {op_type}")
        
        return OPERATORS[op_type](left, right)
    
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand)
        op_type = type(node.op)
        
        if op_type not in OPERATORS:
            raise ValueError(f"不支持的一元运算符: {op_type}")
        
        return OPERATORS[op_type](operand)
    
    else:
        raise ValueError(f"不支持的表达式类型: {type(node)}")


@tool
def calculator(expression: str) -> str:
    """
    计算数学表达式
    
    支持的运算：加(+)、减(-)、乘(*)、除(/)、幂(**)、取模(%)、整除(//)
    
    Args:
        expression: 数学表达式字符串，例如 "2 + 3 * 4"
    
    Returns:
        计算结果的字符串表示
    """
    try:
        logger.info(f"计算表达式: {expression}")
        
        # 解析表达式为 AST
        tree = ast.parse(expression, mode="eval")
        
        # 安全求值
        result = _safe_eval(tree.body)
        
        logger.info(f"计算结果: {result}")
        return str(result)
    
    except SyntaxError as e:
        logger.error(f"表达式语法错误: {str(e)}")
        return f"语法错误: {str(e)}"
    
    except ValueError as e:
        logger.error(f"表达式求值错误: {str(e)}")
        return f"求值错误: {str(e)}"
    
    except ZeroDivisionError:
        logger.error("除零错误")
        return "错误: 除数不能为零"
    
    except Exception as e:
        logger.error(f"计算失败: {str(e)}")
        return f"计算失败: {str(e)}"


def create_calculator_tool():
    """创建计算器工具"""
    return calculator

