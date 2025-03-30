# 高级魔方求解算法实现
import numpy as np
import copy as cp

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

# 高级求解函数
def solve_advanced(faces, encode_cube_func, is_init_state_func, solve_cube_func):
    """使用高级二阶段算法求解魔方，步数少于标准算法"""
    try:
        import kociemba
        has_kociemba = True
    except ImportError:
        has_kociemba = False
        print("警告：kociemba库未安装，将回退到标准解法")
    
    # 获取当前状态的副本
    current_faces = cp.deepcopy(faces)
    
    # 首先检查魔方是否需要求解
    if is_init_state_func(current_faces):
        print("魔方已是完成状态，无需求解")
        return []
    
    # 尝试使用kociemba的高级参数求解（增加搜索深度和启发式参数）
    if has_kociemba:
        try:
            # 生成kociemba输入
            cube_str = encode_cube_func(current_faces)
            print(f"kociemba输入: {cube_str}")
            
            # 尝试提供多种选项，选择最短的解法
            print("使用高级算法求解，正在尝试多种搜索参数...")
            
            # 存储不同解法尝试的结果
            solutions = []
            
            try:
                # 方法1: 标准二阶段算法，设置较大深度
                print("尝试深度搜索算法...")
                solution_deep = kociemba.solve(cube_str, 25)
                steps_deep = solution_deep.split()
                print(f"深度搜索算法步数: {len(steps_deep)}")
                solutions.append((steps_deep, f"深度搜索算法 ({len(steps_deep)}步)"))
            except Exception as e:
                print(f"深度搜索算法失败: {str(e)}")
            
            try:
                # 方法2: 使用最大深度
                print("尝试最大深度搜索...")
                solution_max = kociemba.solve(cube_str, 30)
                steps_max = solution_max.split()
                print(f"最大深度搜索步数: {len(steps_max)}")
                solutions.append((steps_max, f"最大深度搜索 ({len(steps_max)}步)"))
            except Exception as e:
                print(f"最大深度搜索失败: {str(e)}")

            # 如果有可用的解法，选择步骤最少的
            if solutions:
                # 按步骤数排序
                solutions.sort(key=lambda x: len(x[0]))
                best_solution, method_name = solutions[0]
                
                print(f"\n找到最优解法: {method_name}")
                print(f"解法步骤: {' '.join(best_solution)}")
                
                # 执行一些优化，去除冗余步骤
                optimized_steps = optimize_solution(best_solution)
                
                if len(optimized_steps) < len(best_solution):
                    print(f"优化后步数: {len(optimized_steps)} (减少了 {len(best_solution) - len(optimized_steps)} 步)")
                    print(f"优化后解法: {' '.join(optimized_steps)}")
                    return optimized_steps
                else:
                    return best_solution
            else:
                print("高级算法尝试失败，回退到标准算法")
                
        except Exception as e:
            print(f"高级算法出错: {str(e)}")
    
    # 如果高级算法失败，回退到标准的求解算法，但也应用优化
    print("使用标准算法求解...")
    standard_solution = solve_cube_func(faces)
    
    # 应用优化到标准解法
    if standard_solution:
        optimized_standard = optimize_solution(standard_solution)
        print(f"标准算法步数: {len(standard_solution)}")
        if len(optimized_standard) < len(standard_solution):
            print(f"优化后标准算法步数: {len(optimized_standard)} (减少了 {len(standard_solution) - len(optimized_standard)} 步)")
            return optimized_standard
        return standard_solution
    
    return [] 