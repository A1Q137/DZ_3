from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["cats_and_quotes_db"]
cats_collection = db["cats"]
authors_collection = db["authors"]
quotes_collection = db["quotes"]

def create_cat(name, age, features):
    try:
        cat = {"name": name, "age": age, "features": features}
        result = cats_collection.insert_one(cat)
        print(f"Кот добавлен с ID: {result.inserted_id}")
    except Exception as e:
        print(f"Ошибка: {e}")

def read_all_cats():
    try:
        cats = cats_collection.find()
        for cat in cats:
            print(cat)
    except Exception as e:
        print(f"Ошибка: {e}")

def read_cat_by_name(name):
    try:
        cat = cats_collection.find_one({"name": name})
        if cat:
            print(cat)
        else:
            print("Кот с таким именем не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def update_cat_age(name, new_age):
    try:
        result = cats_collection.update_one({"name": name}, {"$set": {"age": new_age}})
        if result.modified_count > 0:
            print("Возраст кота обновлен.")
        else:
            print("Кот с таким именем не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def add_feature_to_cat(name, feature):
    try:
        result = cats_collection.update_one({"name": name}, {"$push": {"features": feature}})
        if result.modified_count > 0:
            print("Характеристика добавлена.")
        else:
            print("Кот с таким именем не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def delete_cat_by_name(name):
    try:
        result = cats_collection.delete_one({"name": name})
        if result.deleted_count > 0:
            print("Кот удален.")
        else:
            print("Кот с таким именем не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

def delete_all_cats():
    try:
        cats_collection.delete_many({})
        print("Все записи удалены.")
    except Exception as e:
        print(f"Ошибка: {e}")

def scrape_quotes():
    base_url = "http://quotes.toscrape.com"
    authors = {}
    quotes = []

    page = 1
    while True:
        response = requests.get(f"{base_url}/page/{page}/")
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes_elements = soup.select(".quote")

        for quote in quotes_elements:
            text = quote.find("span", class_="text").get_text(strip=True)
            author = quote.find("small", class_="author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote.select(".tags .tag")]

            quotes.append({"tags": tags, "author": author, "quote": text})

            if author not in authors:
                author_link = base_url + quote.find("a")["href"]
                author_response = requests.get(author_link)
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                born_date = author_soup.find(class_="author-born-date").get_text(strip=True)
                born_location = author_soup.find(class_="author-born-location").get_text(strip=True)
                description = author_soup.find(class_="author-description").get_text(strip=True)

                authors[author] = {
                    "fullname": author,
                    "born_date": born_date,
                    "born_location": born_location,
                    "description": description
                }

        page += 1

    with open("quotes.json", "w", encoding="utf-8") as q_file:
        json.dump(quotes, q_file, ensure_ascii=False, indent=4)

    with open("authors.json", "w", encoding="utf-8") as a_file:
        json.dump(list(authors.values()), a_file, ensure_ascii=False, indent=4)

    print("Данные сохранены в quotes.json и authors.json.")
    try:
        quotes_collection.insert_many(quotes)
        authors_collection.insert_many(list(authors.values()))
        print("Данные импортированы в MongoDB.")
    except Exception as e:
        print(f"Ошибка при импорте данных: {e}")

if __name__ == "__main__":
    while True:
        print("\nВыберите действие:")
        print("1. Создать кота")
        print("2. Прочитать всех котов")
        print("3. Найти кота по имени")
        print("4. Обновить возраст кота")
        print("5. Добавить характеристику коту")
        print("6. Удалить кота по имени")
        print("7. Удалить всех котов")
        print("8. Собрать цитаты и авторов")
        print("9. Выйти")

        choice = input("Введите номер действия: ")
        if choice == "1":
            name = input("Введите имя кота: ")
            age = int(input("Введите возраст кота: "))
            features = input("Введите характеристики через запятую: ").split(", ")
            create_cat(name, age, features)
        elif choice == "2":
            read_all_cats()
        elif choice == "3":
            name = input("Введите имя кота: ")
            read_cat_by_name(name)
        elif choice == "4":
            name = input("Введите имя кота: ")
            new_age = int(input("Введите новый возраст кота: "))
            update_cat_age(name, new_age)
        elif choice == "5":
            name = input("Введите имя кота: ")
            feature = input("Введите новую характеристику: ")
            add_feature_to_cat(name, feature)
        elif choice == "6":
            name = input("Введите имя кота: ")
            delete_cat_by_name(name)
        elif choice == "7":
            delete_all_cats()
        elif choice == "8":
            scrape_quotes()
        elif choice == "9":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор.")