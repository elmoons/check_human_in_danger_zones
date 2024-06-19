import streamlit as st
import io
from PIL import Image
import os
import tempfile
import streamlit as st
from predict import main, process_image, process_video


# Функция для загрузки медиа-файлов
def load_media():
    uploaded_file = st.file_uploader(label="Выберите изображение или видео",
                                     type=['jpg', 'jpeg', 'png', 'bmp', 'mp4', 'avi', 'mov'])
    if uploaded_file is not None:
        file_type = uploaded_file.type.split('/')[0]  # image или video

        if file_type == 'image':
            # Сохранение изображения в заданную папку
            save_folder = 'save_media/image'  # Замените на путь к вашей папке сохранения
            save_uploaded_file(uploaded_file, save_folder)
            st.success(f'Файл "{uploaded_file.name}" успешно отправлен.')
            image_data = uploaded_file.getvalue()
            st.image(image_data)
            return Image.open(io.BytesIO(image_data)), 'image', uploaded_file.name
        elif file_type == 'video':
            save_folder = 'save_media/video'
            save_uploaded_file(uploaded_file, save_folder)
            st.success(f'Файл "{uploaded_file.name}" успешно отправлен.')
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            st.video(tfile.name)
            return tfile.name, 'video', uploaded_file.name
    else:
        return None, None, None


# Функция для сохранения загруженного файла
def save_uploaded_file(uploaded_file, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    with open(os.path.join(save_folder, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


# Функция для отправки обработанного файла пользователю
def send_processed_file(processed_file, folder):
    file_path = os.path.join(folder, processed_file)
    with open(file_path, "rb") as file:
        file_bytes = file.read()
        st.download_button(
            label=f"Download {processed_file}",
            data=file_bytes,
            file_name=processed_file,
            mime="application/octet-stream"
        )


# Функция для предсказания
def predict(file_name, media_type):
    user_input = st.text_input("Введите координаты опасной зоны. Например: (100, 100) (900, 200) (700, 800) (100, 700)")
    if st.button("Распознать"):
        # Здесь вы можете добавить вашу логику обработки изображения или видео
        is_in_danger = main(file_name, user_input, media_type)
        if media_type == "image":
            processed_folder = 'results/processed_images'  # Замените на путь к вашей папке с обработанными файлами
            send_processed_file(f"{file_name}_processed.jpg", processed_folder)
        elif media_type == "video":
            processed_folder = 'results/processed_videos'
            send_processed_file(f"{file_name}_processed.mp4", processed_folder)
        if is_in_danger:
            st.write("Человек в опасной зоне.")
        else:
            st.write("Человек в безопасной зоне.")


# Основная часть приложения Streamlit
st.title("Обнаружение людей в опасных зонах на производстве.")
media, media_type, file_name = load_media()

if media is not None and media_type == 'image':
    st.write("Загружено изображение")
    predict(file_name, media_type)
elif media is not None and media_type == 'video':
    st.write("Загружено видео")
    predict(file_name, media_type)
else:
    st.write("Файл не загружен или неподдерживаемый формат")
