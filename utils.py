import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# @st.cache_data
# def convert_m4a_to_mp3(input_file_path: str, output_file_path: str):
#   os.system(f"ffmpeg -i {input_file_path} -c:v copy -c:a libmp3lame -q:a 4 {output_file_path}")

@st.cache_data
def transcribe(audio_file):
  return openai.Audio.transcribe("whisper-1", audio_file)

@st.cache_data
def segmentation(long_text: str):
  min_length = 1000
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
  
  completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {
              "role": "user",
              "content": content
          }
      ]
  )

  return completion.choices[0].message.content

@st.cache_data
def create_title(text: str):
  prompt = "次の内容に合うタイトルを書いてください"
  content = f"{prompt}:「{text}」"
  
  completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {
              "role": "user",
              "content": content
          }
      ]
  )

  return completion.choices[0].message.content

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