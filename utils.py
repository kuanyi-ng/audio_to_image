import streamlit as st
import openai
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_completion(prompt: str, model: str = 'gpt-4'):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            },
        ]
    )

    return completion.choices[0].message.content

@st.cache_data
def translate_to_en(text: str):
    prompt = f"このテキストを英語に翻訳してください\n```\n{text}\n```"

    return chat_completion(prompt)

@st.cache_data
def transcribe(audio_file):
    return openai.Audio.transcribe("whisper-1", audio_file)

@st.cache_data
def fix_transcript(transcript: str):
    prompt = f"以下の文章を文法的に正しく、そして自然に聞こえるように日本語で体言止めや接続詞を適宜使いながら修正してください。\
    ```\
    {transcript}\
    ```"

    return chat_completion(prompt)

@st.cache_data
def segmentation(long_text: str, min_length: int):
    segmented_texts = []

    start_idx = 0

    try:
        while True:
            space_idx = long_text.index(" ", start_idx+min_length)

            curr_segment = long_text[start_idx:space_idx]

            segmented_texts.append(curr_segment)

            start_idx = space_idx + 1
    except ValueError:
        # 最後まで分割した
        segmented_texts.append(long_text[start_idx:])

    return segmented_texts

@st.cache_data
def summarize(text: str, length: int = 300):
    if len(text) < length:
        length = len(text)

    num_main_points = (len(text) / 2000 * 5) // 1

    prompt = f"""
    # 命題
    テキストの要約をしようとしています。
    次の要約ステップに沿って文章を要約し、出力してください。
  
    # 要約ステップ
    1. テキストから重要な発言を{num_main_points}箇所抽出する
    2. ステップ1で抽出したそれぞれの箇所について、前後の文脈を汲み取りながら説明を付け加える
    3. ステップ2で説明を加えた{num_main_points}箇所を全て結合する
    4. ステップ3で結合した文章を新聞記事のような体裁に{length}字程度に要約する

    # テキスト
    {text}

    # 出力
    ここに要約ステップ4の要約内容を出力してください。
"""

    return chat_completion(prompt)

@st.cache_data
def segment_and_summarize(long_text: str, segmentation_min_length: int):
    segmented_texts = segmentation(long_text, segmentation_min_length)

    segmented_summary = []
    for segment in segmented_texts:
        segmented_summary.append(summarize(segment))

        sleep(1) # sleep to avoid rate limit

    return segmented_summary

@st.cache_data
def create_title(text: str):
    prompt = f"""この文章から15文字程度で簡潔に記事タイトルを出力してください。
        ```
        {text}
        ```"""
  
    return chat_completion(prompt)

@st.cache_data
def create_image_prompt(text: str, prompt_prefix: str):
    summarized_text = summarize(text, 500)
    text_in_en = translate_to_en(text)
    text_in_en = chat_completion(f"Summarize the following text within 350 characters.\n```\n{summarized_text}\n```")

    return f"{prompt_prefix}, {text_in_en}"

@st.cache_data
def create_images(prompt: str, num_image: int = 4, size: str="512x512"):
    """
    return url to image
    """
    image_response = openai.Image.create(
        prompt=prompt,
        n=num_image,
        size=size
    )

    return [image['url'] for image in image_response['data']]
