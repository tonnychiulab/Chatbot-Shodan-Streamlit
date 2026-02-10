import streamlit as st
import shodan
from openai import OpenAI

# 設定頁面資訊
st.set_page_config(page_title="my-tiny-audit", page_icon="🔍")
st.title("🔍 my-tiny-audit")
st.caption("🚀 整合 Shodan 測繪與 OpenAI 智慧分析的資安稽核工具")

# --- 側邊欄：API 金鑰設定 ---
with st.sidebar:
    st.header("設定")
    shodan_api_key = st.text_input("Shodan API Key", type="password", placeholder="請輸入您的 Shodan API Key")
    openai_api_key = st.text_input("OpenAI API Key", type="password", placeholder="請輸入您的 OpenAI API Key")
    
    st.markdown("---")
    st.markdown("### 關於 my-tiny-audit")
    st.info("這是一個輕量化的資安工具，透過外部測繪數據進行自動化稽核。")

# --- 主介面邏輯 ---
target = st.text_input("輸入稽核目標 (IP 或 網域名稱)", placeholder="例如: 8.8.8.8 或 example.com")

if st.button("開始掃描與分析"):
    if not shodan_api_key or not openai_api_key:
        st.error("請在左側選單輸入必要的 API 金鑰。")
    elif not target:
        st.warning("請輸入有效的目標 IP 或網域名稱。")
    else:
        try:
            # 1. 初始化 Shodan 並查詢
            api = shodan.Shodan(shodan_api_key)
            
            with st.spinner("正在從 Shodan 抓取數據..."):
                # 如果輸入的是域名，先做簡單處理或直接讓 shodan 嘗試
                host = api.host(target)
            
            # 2. 顯示 Shodan 基礎數據
            st.subheader(f"📊 外部資產數據: {target}")
            col1, col2 = st.columns(2)
            col1.metric("城市", host.get('city', '未知'))
            col2.metric("組織", host.get('org', '未知'))
            
            with st.expander("查看完整開放連接埠 (Ports)"):
                st.write(host.get('ports', []))
            
            # 3. 呼叫 OpenAI 進行智慧稽核分析
            with st.spinner("AI 正在分析潛在風險..."):
                client = OpenAI(api_key=openai_api_key)
                
                # 準備傳送給 AI 的摘要數據
                shodan_summary = f"IP: {host['ip_str']}, Ports: {host['ports']}, Org: {host.get('org', 'N/A')}, Data: {str(host.get('data', []))[:1000]}"
                
                prompt = f"""
                你是一位資深的資安稽核專家。以下是從 Shodan 獲得的掃描數據：
                {shodan_summary}
                
                請針對以上數據進行 'my-tiny-audit' 安全評估，並提供：
                1. 關鍵風險評等 (高/中/低)
                2. 異常暴露的服務分析
                3. 建議的修復行動
                請使用繁體中文回答。
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader("🤖 AI 稽核報告")
                st.write(response.choices[0].message.content)

        except shodan.APIError as e:
            st.error(f"Shodan API 錯誤: {e}")
        except Exception as e:
            st.error(f"發生錯誤: {e}")
