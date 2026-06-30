# tools.py​
##Agent可以使用的工具集合。
import datetime

class AgentTools:

    @staticmethod
    def search_web(query):
        """模拟网络搜索工具（此处为模拟）"""
        """下面相当于创建了一个字典，包含了一些预设的搜索结果。当调用 search_web 方法时，会根据输入的查询内容在这个字典中查找匹配的结果，并返回相应的信息摘要。"""
        mock_results = {
            "学习资源推荐": "数学、物理、计算机科学经典教材推荐...",
            "上海天气": "今天多云,18-26°C,东南风3级。",
            "Java 教程": "推荐廖雪峰的Java教程,以及《Java核心技术》书籍。"
        }
        for key, value in mock_results.items():
            if key in query:
                return f"[网络搜索] 关于 '{key}' 的结果：{value}"
        return f"[网络搜索] 未找到 '{query}' 的明确信息。"
    
    @staticmethod
    def make_schedule(steps):
        """制定日程计划工具"""
        schedule = "生成的日程计划：\n"
        for i, step in enumerate(steps, 1):
            schedule += f"{i}. {step}\n"
        return schedule
    
    @staticmethod
    def get_current_time():
        """获取当前时间工具"""
        now = datetime.datetime.now()
        return f"[系统时间] 现在是：{now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def calculate(expression):
        """简单计算器工具（安全版本，修复兼容性问题）"""
        try:
            # 1. 严格过滤非法字符（仅允许数字、基础运算符、括号、空格）​
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return "[计算器] 表达式包含非法字符，拒绝计算。"
            
            # 3. 安全执行计算（限制内置函数，仅保留基础运算）​
            # 自定义安全的全局环境，仅允许基础数学运算
            clean_expr = expression.strip().replace(" ", "")
            if not clean_expr:
                return "[计算器] 表达式不能为空。"
            
            safe_globals = {
                '__builtins__': {},
                'pow': pow,
                'abs': abs
            }
            # 使用 eval 但严格限制环境，且已过滤非法字符，大幅降低风险​
            result = eval(clean_expr, safe_globals)
            return f"[计算器] {expression} = {result}"
    
        except ZeroDivisionError:
            return "[计算器] 错误：除数不能为零。"
        except SyntaxError:
            return "[计算器] 表达式语法错误（如括号不匹配、运算符错误）。"
        except Exception as e:
            return f"[计算器] 计算错误: {str(e)}"

# 测试工具​
if __name__ == "__main__":
    print(AgentTools.search_web("给我一个Java 教程"))
    print(AgentTools.get_current_time())
    print(AgentTools.calculate("(8 + 2) * 3"))
    print(AgentTools.calculate("15 / 0"))
    print(AgentTools.calculate("__import__('sys').version"))

    
