# 简化版保存函数，用于修复cube.py中的问题

# 将解法步骤保存到文件（简化版本）
def save_solution_to_file(steps):
    """简化版保存步骤到文件函数"""
    if not steps:
        print("没有执行任何步骤，不保存文件")
        return
    
    # 创建文件名，使用时间戳
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cube_solution_{timestamp}.txt"
    
    # 在终端显示完整解法
    print(f"\n完整魔方解法 - 共 {len(steps)} 步（已保存到文件: {filename}）")
    
    # 写入文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"魔方解法步骤 - 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总步数: {len(steps)}\n\n")
        f.write("步骤详情:\n")
        
        # 写入所有步骤
        for i, step in enumerate(steps):
            f.write(f"第 {i+1} 步: {step}\n")
        
        # 写入紧凑版本
        f.write("\n紧凑版本（仅步骤符号）:\n")
        f.write(" ".join(steps) + "\n")
    
    print(f"解法已保存到文件: {filename}")
    return filename 