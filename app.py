import streamlit as st
from openai import OpenAI

# --- 页面设置 ---
st.set_page_config(
    page_title="我的 AI 聊天室",
    page_icon="🤖",
    layout="centered"
)

# --- 侧边栏配置 (设置 API Key 和地址) ---
with st.sidebar:
    st.title("🛠️ 设置栏")
    
    # 1. 输入 API Key (密码模式显示)
    api_key = st.text_input("请输入 OpenAI API Key:", type="password", placeholder="sk-...")
    
    # 2. 输入接口地址 (方便国内用户使用中转)
    base_url = st.text_input("接口地址 (可选)", value="https://api.openai.com/v1", placeholder="例如 https://api.gpt-proxy.com/v1")
    
    # 3. 选择模型
    selected_model = st.selectbox("选择模型", ["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"])
    
    # 4. 清空历史按钮
    if st.button("🗑️ 清空对话记录"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.info("提示：如果在中国大陆，请务必修改'接口地址'为中转地址。")

# --- 主聊天界面逻辑 ---

st.title("🤖 私人 ChatGPT 网页版")

# 1. 初始化 API 客户端
if not api_key:
    st.warning("请在左侧侧边栏输入 API Key 才能开始聊天。")
    st.stop()

try:
    client = OpenAI(api_key=api_key, base_url=base_url)
except Exception as e:
    st.error(f"客户端初始化失败: {e}")
    st.stop()

# 2. 初始化聊天记录 (Session State)
if "messages" not in st.session_state:
    # 默认系统提示词
    st.session_state.messages = [
        {"role": "system", "content": "你是一个有用的 AI 助手，使用 Markdown 格式回复。"}
    ]

# 3. 渲染之前的聊天记录
# 跳过第一条 system 消息，只显示用户和 AI 的对话
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 4. 处理用户输入
if user_input := st.chat_input("在这里输入你的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    # 加入历史记录
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 5. 调用 API 并生成回复 (流式输出)
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 创建一个占位符
        full_response = ""
        
        try:
            # 发起流式请求
            stream = client.chat.completions.create(
                model=selected_model,
                messages=st.session_state.messages,
                stream=True, # 开启流式
                temperature=0.7
            )
            
            # 实时更新屏幕
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # 加个光标效果
            
            # 最后去除光标
            message_placeholder.markdown(full_response)
            
            # 将完整的 AI 回复加入历史记录
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"发生错误: {e}")