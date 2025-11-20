import streamlit as st
import json
import os

# --- 🔐 配置区域 ---
DATA_FILE = "my_links.json"  # 数据保存在这个文件里
ADMIN_PASSWORD = "admin"      # ⚠️ 修改这里的密码！

# --- 🛠️ 数据处理函数 ---
def load_data():
    """读取数据，如果文件不存在则创建默认数据"""
    if not os.path.exists(DATA_FILE):
        default_data = {
            "🔍 常用搜索": [
                {"name": "百度", "url": "https://www.baidu.com", "desc": "有问题，百度一下"},
                {"name": "Google", "url": "https://www.google.com", "desc": "全球最大搜索引擎"}
            ],
            "🤖 AI 工具": [
                {"name": "ChatGPT", "url": "https://chatgpt.com", "desc": "OpenAI 官方网页"},
                {"name": "Claude", "url": "https://claude.ai", "desc": "Anthropic 出品的强大 AI"}
            ]
        }
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    """保存数据到 JSON 文件"""
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 🖥️ 页面初始化 ---
st.set_page_config(page_title="我的专属导航", page_icon="🚀", layout="wide")
data = load_data() # 加载当前的数据

# --- 👮 侧边栏：管理员登录 & 编辑 ---
with st.sidebar:
    st.title("⚙️ 管理面板")
    
    # 检查是否登录
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    if not st.session_state.is_admin:
        # === 未登录状态 ===
        pwd_input = st.text_input("输入密码进入编辑模式", type="password")
        if st.button("解锁"):
            if pwd_input == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun() # 刷新页面
            else:
                st.error("密码错误！")
    else:
        # === 已登录状态 (显示编辑功能) ===
        st.success("✅ 管理员模式已开启")
        
        if st.button("退出登录"):
            st.session_state.is_admin = False
            st.rerun()
        
        st.markdown("---")
        
        # 1. 添加新链接
        st.subheader("➕ 添加链接")
        categories = list(data.keys())
        
        with st.form("add_link_form"):
            # 如果没有分类，允许新建
            if not categories:
                new_cat_input = st.text_input("新建分类名称")
                use_existing = False
            else:
                # 选择已有分类 或者 新建
                cat_choice = st.radio("选择分类", ["已有分类", "新建分类"])
                if cat_choice == "已有分类":
                    selected_cat = st.selectbox("选择分类", categories)
                else:
                    selected_cat = st.text_input("输入新分类名称")
            
            name = st.text_input("网站名称 (如: 百度)")
            url = st.text_input("网址 (如: https://...)")
            desc = st.text_input("简介 (选填)")
            
            submitted = st.form_submit_button("提交保存")
            
            if submitted:
                if not selected_cat or not name or not url:
                    st.error("请填写完整信息")
                else:
                    if selected_cat not in data:
                        data[selected_cat] = []
                    
                    data[selected_cat].append({
                        "name": name, 
                        "url": url, 
                        "desc": desc
                    })
                    save_data(data)
                    st.success(f"已添加 {name}！")
                    st.rerun()

        st.markdown("---")
        
        # 2. 删除分类功能 (简单粗暴版)
        st.subheader("🗑️ 数据清理")
        del_cat = st.selectbox("选择要删除的分类", ["(不删除)"] + list(data.keys()))
        if del_cat != "(不删除)":
            if st.button(f"确认删除整个【{del_cat}】分类?"):
                del data[del_cat]
                save_data(data)
                st.rerun()

# --- 🖼️ 主页面：展示导航 ---
st.title("🚀 我的超级导航站")

# 简单的搜索框（纯前端过滤）
search = st.text_input("🔍 搜索网站...", "")

# 遍历并显示数据
for category, links in data.items():
    # 搜索过滤逻辑
    filtered_links = [l for l in links if search.lower() in l['name'].lower() or search.lower() in l.get('desc', '').lower()]
    
    if not filtered_links and search: 
        continue # 如果搜索没结果就不显示该分类

    if filtered_links:
        st.header(category)
        
        # 创建多列布局（比如每行显示 4 个卡片）
        cols = st.columns(4)
        
        for i, link in enumerate(filtered_links):
            col = cols[i % 4] # 循环分配到4列中
            with col:
                # 显示卡片风格的内容
                with st.container(border=True):
                    st.markdown(f"**[{link['name']}]({link['url']})**")
                    if link.get('desc'):
                        st.caption(link['desc'])
                    
                    # 如果是管理员，每个卡片下面显示一个小删除按钮
                    if st.session_state.is_admin:
                        if st.button("🗑️", key=f"del_{category}_{i}", help=f"删除 {link['name']}"):
                            data[category].pop(i) # 删除列表中的这一项
                            save_data(data)
                            st.rerun()

if not data:
    st.info("还没数据，请在左侧登录管理员密码，添加你的第一个链接！")