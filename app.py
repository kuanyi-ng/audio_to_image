import streamlit as st

from utils import *

#
# Parameters
#

SEGMENTATION_MIN_LENGTH = 1000
LINER_NOTE_MAX_LENGTH = 1000
IMAGE_PROMPT_MAX_LENGTH = 500

#
# Input
#
st.header("Audio to ZINE")

st.subheader("音声 → テキスト")
# st.markdown(":black_circle_for_record:")
# from audio_recorder_streamlit import audio_recorder

# audio_bytes = audio_recorder(pause_threshold=10.0)
# if audio_bytes:
#     st.audio(audio_bytes, format="audio/wav")

uploaded_file = st.file_uploader("音声データを選ぶ...", type=['mp3', 'm4a', 'wav'])

segmented_transcript = []

if uploaded_file is not None:
    audio_file_path = uploaded_file.name
    
    # 音声データからテキストを起こす
    transcript = transcribe(uploaded_file)

    segmented_transcript = [
        fix_transcript(segment)
        for segment in segmentation(transcript.text, SEGMENTATION_MIN_LENGTH)
    ]

title_and_summary_tab, text_to_image_tab, record_tab = st.tabs(["テキスト → タイトル・要約", "テキスト → 画像", "テキスト → レコードZINE"])

with title_and_summary_tab:
    st.subheader("テキスト → タイトル・要約")
    st.text("選んだ文章をもとにタイトルと要約を生成する")

    # e.g., [True, False, True, False, False, True]
    selected_segments_idx = [
        st.checkbox(segment, key=f"title_and_summary_segment_{segment_i}")
        for segment_i, segment in enumerate(segmented_transcript)
    ]

    # e.g., ['あいうえお', 'かきくけこ', 'さしすせそ']
    selected_segments = [ segmented_transcript[i] for i, selected in enumerate(selected_segments_idx) if selected ]

    #
    # Output
    #
    if st.button('タイトルと要約を生成する！', disabled=len(selected_segments) <= 0):
        text = '\n'.join(selected_segments)

        title = create_title(text)
        summary = summarize(text)

        st.write(f'タイトル: {title}')
        st.write(f'要約:\n{summary}')
        st.write(f'本文:\n{"".join(selected_segments)}')

        json_data = {
            'transcript': transcript.text,
            'title': title,
            'summary': summary,
            'selected_segments': selected_segments,
        }
        st.download_button('出力データをダウンロード', str(json_data), file_name='text_gen.json', mime='application/json')

with text_to_image_tab:
    st.subheader("テキスト → 画像")
    st.text("選んだ文章をもとに画像を生成する")

    # e.g., [True, False, True, False, False, True]
    selected_segments_idx = [
        st.checkbox(segment, key=f"text_to_image_segment_{segment_i}")
        for segment_i, segment in enumerate(segmented_transcript)
    ]

    # e.g., ['あいうえお', 'かきくけこ', 'さしすせそ']
    selected_segments = [ segmented_transcript[i] for i, selected in enumerate(selected_segments_idx) if selected ]

    #
    # Output
    #
    if st.button('画像を生成する！', disabled=len(selected_segments) <= 0):
        text = '\n'.join(selected_segments)

        image_prompt = create_image_prompt(text, "an article cover image")
        image_urls = create_images(image_prompt)

        st.write(f'画像生成プロンプト: {image_prompt}')
        for image_url in image_urls:
            st.image(image_url)
        st.write(f'本文:\n{text}')

        json_data = {
            'transcript': transcript.text,
            'image_prompt': image_prompt,
            'image_urls': image_urls,
            'selected_segments': selected_segments,
        }
        st.download_button('出力データをダウンロード', str(json_data), file_name='image_gen.json', mime='application/json')

with record_tab:
    st.subheader("テキスト → レコードZINE")
    st.text("選んだ文章をもとに、レコードのタイトル、ライナーノート、と画像を生成する")

    # e.g., [True, False, True, False, False, True]
    selected_segments_idx = [
        st.checkbox(segment, key=f"text_to_zine_segment_{segment_i}")
        for segment_i, segment in enumerate(segmented_transcript)
    ]

    # e.g., ['あいうえお', 'かきくけこ', 'さしすせそ']
    selected_segments = [ segmented_transcript[i] for i, selected in enumerate(selected_segments_idx) if selected ]

    #
    # Output
    #
    if st.button('タイトル・ライナーノート・画像を生成する！', disabled=len(selected_segments) <= 0):
        text = '\n'.join(selected_segments)

        title = create_title(text)
        liner_note = '\n'.join(segmented_transcript)
        if len(liner_note) > LINER_NOTE_MAX_LENGTH:
            liner_note = summarize(liner_note)

        # image_text = note if len(note) < IMAGE_PROMPT_MAX_LENGTH else summarize(note)

        st.write(f'タイトル: {title}')
        st.write(f'ライナーノート:\n{liner_note}')

        image_prompt = create_image_prompt(text, "Illustration style for magazine covers")
        image_urls = create_images(image_prompt)
        for image_url in image_urls:
            st.image(image_url)

        st.write(f'本文:\n{text}')

        json_data = {
            'transcript': transcript.text,
            'segmented_transcript': segmented_transcript,
            'title': title,
            'liner_note': liner_note,
            'image_urls': image_urls,
        }
        st.download_button('出力データをダウンロード', str(json_data), file_name='record_jacket.json', mime='application/json')
