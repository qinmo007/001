import streamlit as st
import pandas as pd
import numpy as np
import random
from PIL import Image
import matplotlib.pyplot as plt
import io

# 设置页面配置
st.set_page_config(
    page_title="健康饮食计划生成器",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题和介绍
st.title("🥗 健康饮食计划生成器")
st.markdown("""
这个应用可以帮助你根据个人情况和健康目标生成一个定制化的饮食计划。
填写下面的信息，让我们为你创建一个适合你的健康饮食计划！
""")

# 创建食物数据库
@st.cache_data
def load_food_data():
    import json
    import os
    
    # 定义默认食物数据，当文件不存在时使用
    default_foods = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snacks": []
    }
    
    try:
        # 尝试读取sample_foods.json文件
        with open('sample_foods.json', 'r', encoding='utf-8') as f:
            foods = json.load(f)
            
        # 确保数据结构完整
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            if meal_type not in foods:
                foods[meal_type] = []
                
        return foods
    except FileNotFoundError:
        st.warning("未找到sample_foods.json文件，将使用空的食物数据库")
        return default_foods
    except json.JSONDecodeError:
        st.warning("sample_foods.json文件格式错误，将使用空的食物数据库")
        return default_foods

foods_db = load_food_data()

# 侧边栏 - 用户信息输入
st.sidebar.header("个人信息")

# 基本信息
age = st.sidebar.slider("年龄", 18, 80, 30)
gender = st.sidebar.radio("性别", ["男", "女"])
weight = st.sidebar.number_input("体重 (kg)", 40.0, 150.0, 70.0, 0.1)
height = st.sidebar.number_input("身高 (cm)", 140.0, 220.0, 170.0, 0.1)

# 计算BMI
bmi = weight / ((height/100) ** 2)
bmi_status = ""
if bmi < 18.5:
    bmi_status = "体重过轻"
elif bmi < 24:
    bmi_status = "体重正常"
elif bmi < 28:
    bmi_status = "超重"
else:
    bmi_status = "肥胖"

# 活动水平
activity_levels = {
    "久坐不动": 1.2,
    "轻度活动（每周运动1-3次）": 1.375,
    "中度活动（每周运动3-5次）": 1.55,
    "高度活动（每周运动6-7次）": 1.725,
    "非常活跃（每天高强度运动）": 1.9
}
activity_level = st.sidebar.selectbox("活动水平", list(activity_levels.keys()))
activity_factor = activity_levels[activity_level]

# 健康目标
health_goals = {
    "减肥": -500,
    "维持体重": 0,
    "增肌": 300
}
health_goal = st.sidebar.selectbox("健康目标", list(health_goals.keys()))
calorie_adjustment = health_goals[health_goal]

# 饮食偏好
diet_preferences = st.sidebar.multiselect(
    "饮食偏好",
    ["无特殊偏好", "素食", "高蛋白", "低碳水", "无麸质", "低脂肪"],
    default=["无特殊偏好"]
)

# 过敏原和不喜欢的食物
allergies = st.sidebar.text_area("过敏原或不喜欢的食物（用逗号分隔）", "")
allergies_list = [item.strip().lower() for item in allergies.split(",") if item.strip()]

# 计算每日卡路里需求
def calculate_calories():
    # 基础代谢率 (BMR)
    if gender == "男":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # 总能量消耗 (TDEE)
    tdee = bmr * activity_factor
    
    # 根据健康目标调整卡路里
    adjusted_calories = tdee + calorie_adjustment
    
    return round(adjusted_calories)

daily_calories = calculate_calories()

# 主界面 - 显示用户信息摘要
st.header("你的健康概况")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("BMI", f"{bmi:.1f}", bmi_status)
with col2:
    st.metric("每日卡路里需求", f"{daily_calories} 卡路里")
with col3:
    st.metric("健康目标", health_goal)

# 生成饮食计划
def generate_meal_plan(days=7):
    meal_plan = {}
    
    # 根据饮食偏好过滤食物
    filtered_foods = {}
    for meal_type, foods_list in foods_db.items():
        if "无特殊偏好" in diet_preferences:
            filtered_foods[meal_type] = foods_list
        else:
            filtered_foods[meal_type] = []
            for food in foods_list:
                # 检查食物是否符合任何一个饮食偏好
                if any(pref in food["category"] for pref in diet_preferences):
                    # 检查是否包含过敏原
                    if not any(allergen in food["name"].lower() for allergen in allergies_list):
                        filtered_foods[meal_type].append(food)
    
    # 如果过滤后某类食物为空，使用原始食物列表
    for meal_type, foods_list in filtered_foods.items():
        if not foods_list:
            filtered_foods[meal_type] = foods_db[meal_type]
    
    # 生成每天的饮食计划
    for day in range(1, days + 1):
        day_plan = {
            "breakfast": random.choice(filtered_foods["breakfast"]),
            "lunch": random.choice(filtered_foods["lunch"]),
            "dinner": random.choice(filtered_foods["dinner"]),
            "snacks": [random.choice(filtered_foods["snacks"]), random.choice(filtered_foods["snacks"])]
        }
        
        # 计算每日总营养
        total_calories = day_plan["breakfast"]["calories"] + day_plan["lunch"]["calories"] + day_plan["dinner"]["calories"] + day_plan["snacks"][0]["calories"] + day_plan["snacks"][1]["calories"]
        total_protein = day_plan["breakfast"]["protein"] + day_plan["lunch"]["protein"] + day_plan["dinner"]["protein"] + day_plan["snacks"][0]["protein"] + day_plan["snacks"][1]["protein"]
        total_carbs = day_plan["breakfast"]["carbs"] + day_plan["lunch"]["carbs"] + day_plan["dinner"]["carbs"] + day_plan["snacks"][0]["carbs"] + day_plan["snacks"][1]["carbs"]
        total_fat = day_plan["breakfast"]["fat"] + day_plan["lunch"]["fat"] + day_plan["dinner"]["fat"] + day_plan["snacks"][0]["fat"] + day_plan["snacks"][1]["fat"]
        
        day_plan["nutrition"] = {
            "calories": total_calories,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat
        }
        
        meal_plan[f"第 {day} 天"] = day_plan
    
    return meal_plan

# 生成饮食计划按钮
if st.button("生成我的饮食计划"):
    with st.spinner("正在生成你的个性化饮食计划..."):
        meal_plan = generate_meal_plan(7)  # 生成7天的饮食计划
    
    st.success("饮食计划生成成功！")
    
    # 显示饮食计划
    st.header("你的7天饮食计划")
    
    # 创建选项卡，每个选项卡显示一天的饮食计划
    tabs = st.tabs(list(meal_plan.keys()))
    
    for i, (day, plan) in enumerate(meal_plan.items()):
        with tabs[i]:
            st.subheader(f"{day}的饮食计划")
            
            # 早餐
            st.markdown("### 🍳 早餐")
            st.markdown(f"**{plan['breakfast']['name']}**")
            st.markdown(f"卡路里: {plan['breakfast']['calories']} | 蛋白质: {plan['breakfast']['protein']}g | 碳水: {plan['breakfast']['carbs']}g | 脂肪: {plan['breakfast']['fat']}g")
            
            # 午餐
            st.markdown("### 🥗 午餐")
            st.markdown(f"**{plan['lunch']['name']}**")
            st.markdown(f"卡路里: {plan['lunch']['calories']} | 蛋白质: {plan['lunch']['protein']}g | 碳水: {plan['lunch']['carbs']}g | 脂肪: {plan['lunch']['fat']}g")
            
            # 晚餐
            st.markdown("### 🍲 晚餐")
            st.markdown(f"**{plan['dinner']['name']}**")
            st.markdown(f"卡路里: {plan['dinner']['calories']} | 蛋白质: {plan['dinner']['protein']}g | 碳水: {plan['dinner']['carbs']}g | 脂肪: {plan['dinner']['fat']}g")
            
            # 零食
            st.markdown("### 🍌 零食")
            for snack in plan['snacks']:
                st.markdown(f"**{snack['name']}**")
                st.markdown(f"卡路里: {snack['calories']} | 蛋白质: {snack['protein']}g | 碳水: {snack['carbs']}g | 脂肪: {snack['fat']}g")
            
            # 每日营养总结
            st.markdown("### 📊 每日营养总结")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总卡路里", f"{plan['nutrition']['calories']} 卡路里", f"{plan['nutrition']['calories'] - daily_calories} 卡路里")
            col2.metric("总蛋白质", f"{plan['nutrition']['protein']}g")
            col3.metric("总碳水", f"{plan['nutrition']['carbs']}g")
            col4.metric("总脂肪", f"{plan['nutrition']['fat']}g")
            
            # 营养分布饼图
            st.markdown("### 营养分布")
            # 使用streamlit原生图表API
            protein_cal = plan['nutrition']['protein'] * 4
            carbs_cal = plan['nutrition']['carbs'] * 4
            fat_cal = plan['nutrition']['fat'] * 9
            
            # 创建数据
            chart_data = pd.DataFrame({
                '营养素': ['蛋白质', '碳水', '脂肪'],
                '卡路里': [protein_cal, carbs_cal, fat_cal]
            })
            
            # 使用streamlit的原生图表
            st.bar_chart(chart_data.set_index('营养素'))
            
            # 显示百分比
            total_cal = protein_cal + carbs_cal + fat_cal
            st.markdown(f"**蛋白质**: {protein_cal:.1f} 卡路里 ({protein_cal/total_cal*100:.1f}%)")
            st.markdown(f"**碳水**: {carbs_cal:.1f} 卡路里 ({carbs_cal/total_cal*100:.1f}%)")
            st.markdown(f"**脂肪**: {fat_cal:.1f} 卡路里 ({fat_cal/total_cal*100:.1f}%)")
    
    # 营养趋势分析
    st.header("7天营养趋势分析")
    
    # 提取每天的营养数据
    days = list(meal_plan.keys())
    calories = [plan['nutrition']['calories'] for plan in meal_plan.values()]
    proteins = [plan['nutrition']['protein'] for plan in meal_plan.values()]
    carbs = [plan['nutrition']['carbs'] for plan in meal_plan.values()]
    fats = [plan['nutrition']['fat'] for plan in meal_plan.values()]
    
    # 创建卡路里趋势DataFrame
    cal_df = pd.DataFrame({
        '日期': days,
        '卡路里': calories,
        '目标卡路里': [daily_calories] * len(days)
    }).set_index('日期')
    
    # 显示卡路里趋势
    st.subheader('每日卡路里摄入')
    st.line_chart(cal_df)
    
    # 创建宏量营养素趋势DataFrame
    macro_df = pd.DataFrame({
        '日期': days,
        '蛋白质 (g)': proteins,
        '碳水 (g)': carbs,
        '脂肪 (g)': fats
    }).set_index('日期')
    
    # 显示宏量营养素趋势
    st.subheader('每日宏量营养素摄入')
    st.line_chart(macro_df)
    
    # 添加说明
    st.info(f"目标卡路里摄入量: {daily_calories} 卡路里/天")
    
    # 导出饮食计划
    st.header("导出饮食计划")
    
    # 将饮食计划转换为DataFrame
    meal_plan_data = []
    for day, plan in meal_plan.items():
        meal_plan_data.append({
            "日期": day,
            "早餐": plan['breakfast']['name'],
            "午餐": plan['lunch']['name'],
            "晚餐": plan['dinner']['name'],
            "零食1": plan['snacks'][0]['name'],
            "零食2": plan['snacks'][1]['name'],
            "总卡路里": plan['nutrition']['calories'],
            "总蛋白质(g)": plan['nutrition']['protein'],
            "总碳水(g)": plan['nutrition']['carbs'],
            "总脂肪(g)": plan['nutrition']['fat']
        })
    
    df = pd.DataFrame(meal_plan_data)
    
    # 转换为CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="下载饮食计划 (CSV)",
        data=csv,
        file_name="我的健康饮食计划.csv",
        mime="text/csv",
    )
    
    # 健康提示
    st.header("健康提示")
    tips = [
        "保持充分的水分摄入，每天至少喝8杯水。",
        "尽量选择全食物，减少加工食品的摄入。",
        "均衡摄入各种颜色的蔬菜和水果，以获取多种维生素和矿物质。",
        "控制食物的份量，即使是健康食品也不要过量食用。",
        "规律进餐，避免长时间不吃东西后暴饮暴食。",
        "睡眠充足，良好的睡眠有助于维持健康的新陈代谢。",
        "结合适当的运动，饮食和运动相辅相成。",
        "减少盐和糖的摄入，选择天然调味料。"
    ]
    
    for tip in tips:
        st.markdown(f"- {tip}")

# 添加页脚
st.markdown("---")
st.markdown("© 2023 健康饮食计划生成器 | 由Streamlit强力驱动")
