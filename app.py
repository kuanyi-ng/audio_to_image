import streamlit as st

from utils import *

#
# Parameters
#

SEGMENTATION_MIN_LENGTH = 1000
LINER_NOTE_MAX_LENGTH = 1000
IMAGE_PROMPT_MAX_LENGTH = 500

st.header("音声データから、タイトル、ライナーノート、とジャケットを作成")

uploaded_file = st.file_uploader("音声データを選ぶ...", type=['mp3', 'm4a'])

segmented_summary = []

if uploaded_file is not None:
    audio_file_path = uploaded_file.name
    
    # 音声データからテキストを起こす
    transcript = transcribe(uploaded_file)

    segmented_summary = segment_and_summarize(transcript.text, SEGMENTATION_MIN_LENGTH)

selected_segments_idx = [ st.checkbox(segment) for segment in segmented_summary ]

selected_segments = [ segmented_summary[i] for i, selected in enumerate(selected_segments_idx) if selected ]

#
# Output
#

def generate_output():
    note = '\n'.join(selected_segments)

    title = create_title(note)

    liner_note = '\n'.join(segmented_summary)
    if len(liner_note) > LINER_NOTE_MAX_LENGTH:
        liner_note = summarize(liner_note)

    image_text = note if len(note) < IMAGE_PROMPT_MAX_LENGTH else summarize(note)

    image_url = create_image(image_text, "512x512")

    st.write(f'タイトル: {title}')
    st.write(f'ライナーノート:\n{liner_note}')
    st.write(f'画像のテキスト:\n{image_text}')
    st.image(image_url)
    st.write(f'画像 URL: {image_url}')

    json_data = {
        'title': title,
        'liner_note': liner_note,
        'image_url': image_url,
    }
    st.download_button('出力データをダウンロード', str(json_data), file_name='record_jacket.json', mime='application/json')

st.button('生成する！', on_click=generate_output, disabled=len(selected_segments) <= 0)
