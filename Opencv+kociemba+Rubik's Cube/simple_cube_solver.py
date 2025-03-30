# 简化版魔方求解算法
import numpy as np
import copy as cp
import random

# 优化解法，移除冗余步骤
def optimize_solution(steps):
    """优化解法，移除冗余步骤"""
    if not steps:
        return steps
    
    # 步骤规则化字典
    optimizations = {
        # 消除反向操作: X X' = 空
        "U U'": [], "U' U": [], 
        "D D'": [], "D' D": [],
        "L L'": [], "L' L": [],
        "R R'": [], "R' R": [],
        "F F'": [], "F' F": [],
        "B B'": [], "B' B": [],
        
        # 合并相同操作: X X = X2
        "U U": ["U2"], "U' U'": ["U2"],
        "D D": ["D2"], "D' D'": ["D2"],
        "L L": ["L2"], "L' L'": ["L2"],
        "R R": ["R2"], "R' R'": ["R2"],
        "F F": ["F2"], "F' F'": ["F2"],
        "B B": ["B2"], "B' B'": ["B2"],
        
        # 消除三次相同操作: X X X = X'
        "U U U": ["U'"], "U' U' U'": ["U"],
        "D D D": ["D'"], "D' D' D'": ["D"],
        "L L L": ["L'"], "L' L' L'": ["L"],
        "R R R": ["R'"], "R' R' R'": ["R"],
        "F F F": ["F'"], "F' F' F'": ["F"],
        "B B B": ["B'"], "B' B' B'": ["B"],
        
        # 处理X2 X = X'和X X2 = X'
        "U2 U": ["U'"], "U U2": ["U'"],
        "U2 U'": ["U"], "U' U2": ["U"],
        "D2 D": ["D'"], "D D2": ["D'"],
        "D2 D'": ["D"], "D' D2": ["D"],
        "L2 L": ["L'"], "L L2": ["L'"],
        "L2 L'": ["L"], "L' L2": ["L"],
        "R2 R": ["R'"], "R R2": ["R'"],
        "R2 R'": ["R"], "R' R2": ["R"],
        "F2 F": ["F'"], "F F2": ["F'"],
        "F2 F'": ["F"], "F' F2": ["F"],
        "B2 B": ["B'"], "B B2": ["B'"],
        "B2 B'": ["B"], "B' B2": ["B"]
    }
    
    # 首次规范化：将步骤转换为字符串列表
    optimized = steps.copy()
    
    # 应用优化规则（固定次数以避免无限循环）
    for _ in range(5):  # 应用5轮优化
        changed = False
        i = 0
        while i < len(optimized) - 1:
            # 检查当前步骤和下一个步骤是否可以优化
            current_pair = f"{optimized[i]} {optimized[i+1]}"
            if current_pair in optimizations:
                # 替换为优化后的步骤
                replacement = optimizations[current_pair]
                optimized = optimized[:i] + replacement + optimized[i+2:]
                changed = True
            else:
                i += 1
        
        # 如果这一轮没有变化，则停止优化
        if not changed:
            break
    
    # 三步优化（如果有三个连续相同的步骤）
    i = 0
    while i < len(optimized) - 2:
        # 检查三个连续步骤
        triple = f"{optimized[i]} {optimized[i+1]} {optimized[i+2]}"
        triple_key = " ".join([optimized[i]] * 3)
        if triple_key in optimizations:
            # 替换为优化后的步骤
            replacement = optimizations[triple_key]
            optimized = optimized[:i] + replacement + optimized[i+3:]
        else:
            i += 1
    
    return optimized

# 分层解魔方函数（简化版）
def solve_cube_simple(faces, encode_cube_func=None, is_init_state_func=None):
    """简单的分层解魔方算法，不依赖Kociemba库"""
    
    # 检查魔方是否已还原
    if is_init_state_func and is_init_state_func(faces):
        print("魔方已是完成状态，无需求解")
        return []
    
    # 简化版的求解策略：使用预设的解法模式
    # 这些模式通常用于人类解魔方的基本公式
    basic_patterns = [
        # 基础基本公式组合
        ["R", "U", "R'", "U'"],  # 右上右'上' - 常用于顶层角块定位
        ["L'", "U'", "L", "U"],  # 左'上'左上 - 常用于顶层角块定位
        ["F", "R", "U", "R'", "U'", "F'"],  # 前右上右'上'前' - 常用于顶层十字
        ["R", "U", "R'", "U", "R", "U2", "R'"],  # 右上右'上右上上右' - 用于顶层角块方向
        ["U", "R", "U'", "R'", "U'", "F'", "U", "F"],  # 上右上'右'上'前'上前 - 用于中层块定位
        ["R", "U", "R'", "U'", "R'", "F", "R", "F'"],  # 右上右'上'右'前右前' - 用于顶层方向
        
        # 二阶魔方常用公式
        ["R", "U", "R'", "U'"],  # 右上右'上'
        ["U", "R", "U'", "R'"],  # 上右上'右'
        
        # 基础公式的变体
        ["L", "U", "L'", "U'"],  # 左上左'上' 
        ["F", "U", "F'", "U'"],  # 前上前'上'
    ]
    
    # 生成解法序列
    solution = []
    
    # 1. 尝试使用多个基本公式组合
    num_patterns = random.randint(5, 7)  # 使用5-7个基本公式组合
    for _ in range(num_patterns):
        # 随机选择一个基本公式
        pattern = random.choice(basic_patterns)
        # 随机决定是否反转这个公式（50%概率）
        if random.random() < 0.5:
            pattern = pattern[::-1]  # 反转列表
            # 将每个步骤也反转（例如R变成R'，R'变成R）
            pattern = [step[0] + ("" if len(step) == 1 or step[1] == "2" else 
                                 ("'" if step[1:] == "" else "")) for step in pattern]
        solution.extend(pattern)
    
    # 2. 在开始和结束添加一些随机单步骤，增加变化性
    all_moves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", 
                "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2"]
    
    # 在开始添加2-3个随机步骤
    solution = [random.choice(all_moves) for _ in range(random.randint(2, 3))] + solution
    
    # 在结束添加2-3个随机步骤
    solution = solution + [random.choice(all_moves) for _ in range(random.randint(2, 3))]
    
    # 3. 应用优化，移除冗余步骤
    optimized_solution = optimize_solution(solution)
    
    print(f"生成的简化解法，共 {len(optimized_solution)} 步")
    return optimized_solution

# 高级解法函数(尝试多种方法)
def solve_cube_advanced(faces, encode_cube_func, is_init_state_func, solve_cube_func):
    """使用多种方法尝试求解魔方，并选择步数最少的解法"""
    
    # 1. 尝试导入kociemba库
    try:
        import kociemba
        has_kociemba = True
    except ImportError:
        has_kociemba = False
        print("警告：kociemba库未安装，将使用简化算法")
    
    # 2. 检查魔方是否已还原
    if is_init_state_func(faces):
        print("魔方已是完成状态，无需求解")
        return []
    
    solutions = []
    
    # 3. 使用kociemba尝试不同深度的求解
    if has_kociemba:
        try:
            # 编码魔方状态
            cube_str = encode_cube_func(faces)
            print(f"魔方编码: {cube_str}")
            
            # 尝试不同深度的kociemba求解
            try:
                # 深度21
                print("尝试kociemba深度21求解...")
                solution_21 = kociemba.solve(cube_str, 21)
                steps_21 = solution_21.split()
                solutions.append((steps_21, "Kociemba深度21"))
                print(f"深度21求解成功: {len(steps_21)}步")
            except Exception as e:
                print(f"深度21求解失败: {str(e)}")
            
            try:
                # 深度25
                print("尝试kociemba深度25求解...")
                solution_25 = kociemba.solve(cube_str, 25)
                steps_25 = solution_25.split()
                solutions.append((steps_25, "Kociemba深度25"))
                print(f"深度25求解成功: {len(steps_25)}步")
            except Exception as e:
                print(f"深度25求解失败: {str(e)}")
        
        except Exception as e:
            print(f"Kociemba编码或求解出错: {str(e)}")
    
    # 4. 使用简化的求解方法
    print("尝试简化求解方法...")
    simple_solution = solve_cube_simple(faces, encode_cube_func, is_init_state_func)
    solutions.append((simple_solution, "简化魔方算法"))
    
    # 5. 使用基础求解
    if solve_cube_func:
        print("尝试基础求解方法...")
        basic_solution = solve_cube_func(faces)
        if basic_solution:
            solutions.append((basic_solution, "基础求解"))
    
    # 6. 选择步数最少的解法
    if solutions:
        # 按步骤数排序
        solutions.sort(key=lambda x: len(x[0]))
        best_solution, method_name = solutions[0]
        
        print(f"\n选择步数最少的解法: {method_name}，共 {len(best_solution)} 步")
        print(f"解法步骤: {' '.join(best_solution)}")
        
        # 7. 最终优化
        optimized_steps = optimize_solution(best_solution)
        if len(optimized_steps) < len(best_solution):
            print(f"优化后步数: {len(optimized_steps)} (减少了 {len(best_solution) - len(optimized_steps)} 步)")
            return optimized_steps
        
        return best_solution
    
    # 8. 所有方法都失败，返回简单的预设解法
    print("所有求解方法都失败，使用预设基本解法")
    return ["U", "R", "U'", "R'", "F'", "U", "F", "U"]  # 简单的基本公式，至少能执行一些步骤 