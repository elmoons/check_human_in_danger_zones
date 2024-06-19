import shutil
import os
import random
from shutil import copyfile, rmtree

def distribute_files(input_folder, images_folder, texts_folder):
    # Создаем папки, если они не существуют
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    if not os.path.exists(texts_folder):
        os.makedirs(texts_folder)

    # Получаем список файлов в исходной папке
    files = os.listdir(input_folder)

    # Распределяем файлы по соответствующим папкам
    for file_name in files:
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Файл является изображением - перемещаем в папку с изображениями
            shutil.move(os.path.join(input_folder, file_name), images_folder)
        elif file_name.lower().endswith('.txt'):
            # Файл является текстовым файлом - перемещаем в папку с текстовыми файлами
            shutil.move(os.path.join(input_folder, file_name), texts_folder)



def split_data(photos_dir, annotations_dir, output_photos_dir, output_annotations_dir, val_percentage=0.2):
    # Создание выходных папок, если они не существуют
    os.makedirs(output_photos_dir, exist_ok=True)
    os.makedirs(output_annotations_dir, exist_ok=True)

    # Получение списка файлов с фотографиями в исходной папке
    photo_files = os.listdir(photos_dir)

    # Определение размера валидационного набора
    val_size = int(len(photo_files) * val_percentage)

    # Рандомное выборка фотографий для валидации
    val_photos = random.sample(photo_files, val_size)

    # Копирование выбранных фотографий и соответствующих текстовых файлов в выходные папки
    for photo in val_photos:
        photo_path = os.path.join(photos_dir, photo)
        annotation_path = os.path.join(annotations_dir, photo[:-4] + ".txt")  # Получаем путь к текстовому файлу по имени фотографии
        output_photo_path = os.path.join(output_photos_dir, photo)
        output_annotation_path = os.path.join(output_annotations_dir, photo[:-4] + ".txt")
        copyfile(photo_path, output_photo_path)
        copyfile(annotation_path, output_annotation_path)

        # Удаление скопированных файлов из исходных папок
        os.remove(photo_path)
        os.remove(annotation_path)

    # Удаление исходных папок, если они стали пустыми
    if not os.listdir(photos_dir):
        os.rmdir(photos_dir)
    if not os.listdir(annotations_dir):
        os.rmdir(annotations_dir)



if __name__ == "__main__":
    split_data(r"C:\Users\elmoo\PycharmProjects\danger_zone\data\images\train",
               r"C:\Users\elmoo\PycharmProjects\danger_zone\data\labels\train",
               r"C:\Users\elmoo\PycharmProjects\danger_zone\valid_data\valid_images",
               r"C:\Users\elmoo\PycharmProjects\danger_zone\valid_data\valid_labels")
