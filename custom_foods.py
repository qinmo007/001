import json
import os
import streamlit as st

def load_custom_foods(file_path='sample_foods.json'):
    """
    从JSON文件加载自定义食物数据

    参数:
        file_path: JSON文件的路径

    返回:
        包含食物数据的字典
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                foods = json.load(file)
            return foods
        else:
            st.error(f"文件 {file_path} 不存在")
            return None
    except Exception as e:
        st.error(f"加载食物数据时出错: {str(e)}")
        return None

def merge_food_data(original_foods, custom_foods):
    """
    合并原始食物数据和自定义食物数据

    参数:
        original_foods: 原始食物数据字典
        custom_foods: 自定义食物数据字典

    返回:
        合并后的食物数据字典
    """
    merged_foods = {}

    # 确保所有餐点类型都存在
    for meal_type in set(list(original_foods.keys()) + list(custom_foods.keys())):
        merged_foods[meal_type] = []

        # 添加原始食物
        if meal_type in original_foods:
            merged_foods[meal_type].extend(original_foods[meal_type])

        # 添加自定义食物
        if meal_type in custom_foods:
            merged_foods[meal_type].extend(custom_foods[meal_type])

    return merged_foods

def validate_food_data(foods):
    """
    验证食物数据格式是否正确

    参数:
        foods: 食物数据字典

    返回:
        布尔值，表示数据是否有效
    """
    required_meal_types = ["breakfast", "lunch", "dinner", "snacks"]
    required_food_fields = ["name", "calories", "protein", "carbs", "fat", "category"]

    # 检查必要的餐点类型
    for meal_type in required_meal_types:
        if meal_type not in foods:
            st.error(f"缺少必要的餐点类型: {meal_type}")
            return False

        # 检查每种餐点是否有食物
        if not foods[meal_type]:
            st.error(f"{meal_type} 没有食物项")
            return False

        # 检查每个食物项是否有必要的字段
        for food in foods[meal_type]:
            for field in required_food_fields:
                if field not in food:
                    st.error(f"食物 '{food.get('name', 'Unknown')}' 缺少必要的字段: {field}")
                    return False

    return True

# 如何在应用中使用这些函数的示例
"""
# 在app.py中，将原始的load_food_data函数替换为以下代码:

@st.cache_data
def load_food_data():
    # 尝试加载自定义食物数据
    custom_foods_path = st.sidebar.text_input("自定义食物数据文件路径", "sample_foods.json")
    use_custom_foods = st.sidebar.checkbox("使用自定义食物数据", value=False)
    
    # 默认食物数据
    default_foods = {
        "breakfast": [
            {"name": "燕麦粥", "calories": 150, "protein": 5, "carbs": 27, "fat": 3, "category": ["素食", "无麸质选项"]},
            # ... 其他默认食物 ...
        ],
        # ... 其他餐点类型 ...
    }
    
    if use_custom_foods:
        from custom_foods import load_custom_foods, merge_food_data, validate_food_data
        
        custom_foods = load_custom_foods(custom_foods_path)
        if custom_foods and validate_food_data(custom_foods):
            # 合并默认食物和自定义食物
            return merge_food_data(default_foods, custom_foods)
        else:
            st.warning("使用默认食物数据")
    
    return default_foods
"""

# 如何创建自己的食物数据文件
"""
要创建自己的食物数据文件:

1. 复制 sample_foods.json 文件并重命名
2. 按照相同的格式添加或修改食物项
3. 确保每个食物项都包含以下字段:
   - name: 食物名称
   - calories: 卡路里含量
   - protein: 蛋白质含量(克)
   - carbs: 碳水含量(克)
   - fat: 脂肪含量(克)
   - category: 类别列表(如["素食", "高蛋白"])
4. 在应用中指定自定义食物数据文件路径并启用"使用自定义食物数据"选项
"""

if __name__ == "__main__":
    # 简单的测试代码
    print("测试加载自定义食物数据...")
    foods = load_custom_foods()
    if foods:
        print(f"成功加载食物数据，包含 {len(foods['breakfast'])} 个早餐选项，{len(foods['lunch'])} 个午餐选项，{len(foods['dinner'])} 个晚餐选项，和 {len(foods['snacks'])} 个零食选项。")
    else:
        print("加载食物数据失败")
