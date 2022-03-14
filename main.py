from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# pip install openpyxl

"""
Парсер торговой площидки Юла, с помощью Selenium
Для работоспособности не забудьте скачать сам драйвер, под свою версию браузера Chrome.
Если столкнетесь с капчей, пишите разберемся, в данном примере эту функцию не реализовал
По всем возникшим вопросам, можете писать в группу https://vk.com/happython
Отзывы, предложения, советы приветствуются.
"""


def get_content_page(html):
    """Функция сбора данных с прогружаемой страницы"""
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', {"data-test-component": "ProductOrAdCard"})
    data_list = []
    for block in blocks:
        try:
            name = block.find('span', {'data-test-block': "ProductName"}).text
        except:
            name = 'нет названия'
        try:
            city = block.find('div', {'data-test-component': "Badges"}).text.split('%')[-1]
        except:
            city = 'город не указан'
        try:
            discount = block.find('div', {'data-test-component': "Badges"}).text
            if '%' in discount:
                discount = discount.split('%')[0]
            else:
                discount = ''
        except:
            discount = ''
        try:
            price = block.find('p', {'data-test-block': "ProductPrice"}).text.replace('₽руб.', '').replace('\xa0', '')
        except:
            price = 'нет цены'
        try:
            link = "https://youla.ru" + block.find('div').find('span').find('a').get('href')
        except:
            link = 'ссылка не найдена'

        if 'нет названия' in name:
            pass
        else:
            # print(name)
            # print(city)
            # print(price)
            # print(discount)
            # print(link)
            # print('-----------')

            data_list.append({
                'name': name,
                'city': city,
                'price': price,
                'discount': discount,
                'link': link
            })
    return data_list


def parser(url, data_list_count):
    """Основная функция, сам парсер"""
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0")
    options.add_argument('--log-level=3')
    options.add_argument("--headless")

    # укажите путь до драйвера
    browser = webdriver.Chrome("chromedriver", options=options)

    try:
        browser.get(url)
        time.sleep(2)
        # находим высоту прокрутки
        last_height = browser.execute_script("return document.body.scrollHeight")
        # нажимаем page down для прогрузки первого блока
        browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        data_list_pages = []
        while True:
            data_list_pages.extend(get_content_page(browser.page_source))

            # скролим один раз
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Ждем прогрузки страницы
            time.sleep(2)

            # Вычисляем новую высоту прокрутки и сравниваем с последней высотой прокрутки
            new_height = browser.execute_script("return document.body.scrollHeight")
            if data_list_count == '':
                data_list_count = 1000
            if new_height == last_height:
                break
            last_height = new_height
            print(f'Собрано {len(data_list_pages)} позиций')
            if len(data_list_pages) >= int(data_list_count):
                break
        return data_list_pages

    except Exception as ex:
        print('Не предвиденная ошибка:', ex)
        browser.close()
        browser.quit()
    browser.close()
    browser.quit()


def save_exel(data):
    """Функция сохранения в файл"""
    dataframe = pandas.DataFrame(data)
    writer = pandas.ExcelWriter(f'data_yula.xlsx')
    dataframe.to_excel(writer, 'data_yula')
    writer.save()
    print(f'Сбор данных завершен. Данные сохранены в файл "data_yula.xlsx"')



if __name__ == "__main__":
    url = input('Введите ссылку на раздел, с заранее выбранными характеристиками (ценовой диапазон, сроки размещения и тд):\n')
    data_list_count = input('Примерное количество записей выдачи (или Enter, органичение по умолчанию 1000):\n')
    print('Запуск парсера...')
    save_exel(parser(url, data_list_count))

