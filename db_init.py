from db.qdrant.qdrant_database import QdrantDatabase
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm
from qdrant_client import models
from sentence_transformers import SentenceTransformer
from consts import EMBEDDING_MODEL, MEDIA_WIKI_API_URL, PROJECT_NAME
import requests
from icecream import ic
from db.db_config import qdrant_database
class DBInit:
    def __init__(self, qdrant_db: QdrantDatabase ):
        self.db = qdrant_db
        self.model = SentenceTransformer(EMBEDDING_MODEL)


    def parse_wiki_page(self, html_content):
        """Анализируем структуру страницы и извлекаем данные"""
        soup = BeautifulSoup(html_content, "html.parser")
        result = {
            "classes": [],
            "methods": []
        }
        
        # Обрабатываем все заголовки
        current_class = None
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            if heading.name == 'h5' and 'Класс' in heading.get_text():
                # Обработка класса
                class_name = heading.find('span', class_='mw-headline').get_text(strip=True)
                path_p = heading.find_next('p')
                
                if path_p and 'Путь:' in path_p.get_text():
                    path_text = path_p.get_text().replace('Путь:', '').strip()
                    file_path, line_number = self.parse_path(path_text)
                    
                    # Получаем описание класса
                    description = []
                    next_node = path_p.next_sibling
                    while next_node and next_node.name not in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        if next_node.name == 'p':
                            text = next_node.get_text(strip=True)
                            if text and not text.startswith(('Путь:', 'Декораторы:')):
                                description.append(text)
                        next_node = next_node.next_sibling
                    
                    if description or True:  # Сохраняем даже без описания
                        current_class = {
                            "name": class_name.split()[1],
                            "file_path": file_path,
                            "line_number": line_number,
                            "description": ' '.join(description) if description else None
                        }
                        result["classes"].append(current_class)
            
            elif heading.name == 'h5' and ('Метод' in heading.get_text() or 'Функция' in heading.get_text()):
                # Обработка метода
                method_name = heading.find('span', class_='mw-headline').get_text(strip=True)
                path_p = heading.find_next('p')
                
                if path_p and ('Путь:' in path_p.get_text() or 'path:' in path_p.get_text().lower()):
                    path_text = path_p.get_text().replace('Путь:', '').replace('path:', '').strip()
                    file_path, line_number = self.parse_path(path_text)
                    
                    # Получаем описание метода
                    description = []
                    next_node = path_p.next_sibling
                    while next_node and next_node.name not in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        if next_node.name in ['p', 'ul']:
                            text = next_node.get_text(' ', strip=True)
                            if text and not text.startswith(('Путь:', 'Декораторы:', 'path:')):
                                description.append(text)
                        next_node = next_node.next_sibling
                    
                    if description or True:  # Сохраняем даже без описания
                        method_data = {
                            "name": method_name.split()[1],
                            "file_path": file_path,
                            "line_number": line_number,
                            "description": ' '.join(description) if description else None
                        }
                        
                        # Добавляем ссылку на класс, если он был найден
                        if current_class:
                            method_data["class"] = current_class["name"]
                        
                        result["methods"].append(method_data) 
        return result
            
    def parse_path(self, path_text):
        """Разбираем строку пути на файл и номер строки"""
        if not path_text:
            return None, None
        
        # Ищем шаблоны типа: #services\mail_scheduler_job_service.py:13
        match = re.search(r'(.+?\.py):?(\d+)?$', path_text.replace('\\', '/'))
        if match:
            file_path = match.group(1)
            line_number = int(match.group(2)) if match.group(2) else None
            return file_path, line_number
        return None, None
    

    def save_to_json_and_vector_db(self, data, json_filename):
        """Сохраняем данные в JSON файл и векторную БД"""
        try:
            # Сохранение в JSON
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Данные успешно сохранены в {json_filename}")
            
            # Подготовка точек для векторной БД
            points = []
            point_id = 1
            
            # Обрабатываем классы
            for cls in tqdm(data["classes"], desc="Обработка классов"):
                if not cls.get("description"):
                    continue
                    
                # Генерация эмбеддинга
                text = f"{cls['description']}"
                embedding = self.model.encode(text).tolist()
                
                points.append(models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "type": "class",
                        "name": cls["name"],
                        "file_path": cls["file_path"],
                        "line_number": cls["line_number"],
                        "text": text
                    }
                ))
                point_id += 1
            
            # Обрабатываем методы
            for method in tqdm(data["methods"], desc="Обработка методов"):
                if not method.get("description"):
                    continue
                    
                text = f"{method['description']}"
                embedding = self.model.encode(text).tolist()
                
                points.append(models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "type": "method",
                        "name": method["name"],
                        "class": method.get("class"),
                        "file_path": method["file_path"],
                        "line_number": method["line_number"],
                        "text": text
                    }
                ))
                point_id += 1
            
            # Загрузка данных в Qdrant
            if points:
                self.db.save_data(points)
            else:
                print("Нет данных для загрузки в векторную БД")
                
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")

    def get_wiki_html(self, page_title):
        """Получаем HTML страницы через API"""
        params = {
            "action": "parse",
            "page": page_title,
            "prop": "text",
            "format": "json"
        }
        try:
            response = requests.get(MEDIA_WIKI_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["parse"]["text"]["*"]
        except Exception as e:
            print(f"Ошибка при получении страницы {page_title}: {e}")
            return None
        

    def parse_html_to_structure(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        def parse_list(items, indent=0):
            result = []
            for item in items:
                # Найти текст в toctext
                text = item.select_one('.toctext').text if item.select_one('.toctext') else ''
                # Найти номер в tocnumber
                number = item.select_one('.tocnumber').text if item.select_one('.tocnumber') else ''

                # Формировать строку с отступом
                line = f"{'    ' * indent}{number}\t{text}"
                result.append(line)

                # Обрабатывать вложенные списки
                sub_list = item.find('ul')
                if sub_list:
                    sub_items = sub_list.find_all('li', recursive=False)
                    result.extend(parse_list(sub_items, indent + 1))
            return result

        # Найти элементы верхнего уровня
        top_level_items = soup.find_all('li', class_='toclevel-1 tocsection-1')
        ic(top_level_items)
        project_structure_lines = parse_list(top_level_items)

        # Объединить результат в строку
        return '\n'.join(project_structure_lines)
if __name__ == "__main__":
    db_init = DBInit(qdrant_database)
    html_content = db_init.get_wiki_html(PROJECT_NAME)
    data = db_init.parse_wiki_page(html_content)
    db_init.save_to_json_and_vector_db(data, f"wiki_{PROJECT_NAME.lower()}_embeddings.json")
    # project_structure = db_init.get_wiki_html(PROJECT_NAME)
    # structure = db_init.parse_html_to_structure(project_structure)
    # with open("project_structure_structure.txt", "w", encoding="utf-8") as f:
    #     f.write(structure)
    # ic(structure)