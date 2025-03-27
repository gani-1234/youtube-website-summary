import streamlit as st
import validators
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from youtube_transcript_api import YouTubeTranscriptApi

# Streamlit setup
st.set_page_config(page_title="Gemini Summarizer", page_icon="✨")
st.title("Summarize YouTube Videos & Websites with Gemini 1.5 Flash")

# ✅ Preserve API key and URL input
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "url" not in st.session_state:
    st.session_state.url = ""

# Sidebar input
with st.sidebar:
    st.session_state.api_key = st.text_input("Google Gemini API Key", value=st.session_state.api_key, type="password")

st.session_state.url = st.text_input("Enter YouTube or Website URL", value=st.session_state.url, placeholder="Paste the URL here")

# Define the summary prompt
prompt = """
    Summarize the given content in 300 words:
    Content: {text}
"""
final_prompt = PromptTemplate(input_variables=["text"], template=prompt)

if st.button("Summarize"):
    if not st.session_state.api_key:
        st.error("Please provide a valid Google Gemini API key.")
    elif not validators.url(st.session_state.url):
        st.error("Please provide a valid YouTube or website URL.")
    else:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        content_text = ""
        url = st.session_state.url

        try:
            if "youtube.com" in url or "youtu.be" in url:
                # ✅ Handle YouTube Summarization
                video_id = url.split("v=")[-1].split("&")[0]  # Extract YouTube video ID

                try:
                    with st.spinner("Fetching transcript..."):
                        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
                        data = loader.load()
                        content_text = data[0].page_content  # Extract text
                except:
                    try:
                        with st.spinner("Using alternative method..."):
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                            content_text = " ".join([entry["text"] for entry in transcript])
                    except:
                        st.error("❌ Unable to retrieve transcript. The video may not have subtitles.")
            
            else:
                # ✅ Handle Website Summarization
                with st.spinner("Fetching website content..."):
                    loader = UnstructuredURLLoader(urls=[url], ssl_verify=True, headers={"User-Agent": "Mozilla/5.0"})
                    data = loader.load()
                    content_text = data[0].page_content  # Extract text

            if content_text:
                with st.spinner("Generating summary..."):
                    response = model.generate_content(final_prompt.format(text=content_text))
                st.success(response.text)  # ✅ Display Summary

        except Exception as e:
            st.error(f"❌ Error: {e}")
