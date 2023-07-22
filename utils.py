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
def summarize(text: str):
    prompt = "次の内容を4文以内でまとめてください"
    content = f"{prompt}:「{text}」"

    return chat_completion(content)

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
    prompt = "次の文章から雑誌の対談風記事の見出しを出力してください"
    content = f"{prompt}:「{text}」"
  
    return chat_completion(content)

@st.cache_data
def create_image(prompt: str, size:str="1024x1024"):
    """
    return url to image
    """
    image_response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size
    )

    return image_response['data'][0]['url']

# def generate_jacket_output():
#     note = '\n'.join(selected_segments)

#     title = create_title(note)

#     liner_note = '\n'.join(segmented_summary)
#     if len(liner_note) > LINER_NOTE_MAX_LENGTH:
#         liner_note = summarize(liner_note)

#     image_text = note if len(note) < IMAGE_PROMPT_MAX_LENGTH else summarize(note)

#     image_url = create_image(image_text, "512x512")

#     st.write(f'タイトル: {title}')
#     st.write(f'ライナーノート:\n{liner_note}')
#     st.write(f'画像のテキスト:\n{image_text}')
#     st.image(image_url)
#     st.write(f'画像 URL: {image_url}')

#     json_data = {
#         'transcript': transcript.text,
#         'segmented_summary': segmented_summary,
#         'title': title,
#         'liner_note': liner_note,
#         'image_url': image_url,
#     }
#     st.download_button('出力データをダウンロード', str(json_data), file_name='record_jacket.json', mime='application/json')
