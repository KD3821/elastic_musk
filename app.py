from flask import Flask, render_template, url_for, redirect, request, flash, Markup
from flask.views import MethodView #добавил для бота
import requests                    #добавил для бота
import os                          #добавил для бота
import re                          #добавил для бота
# from dotenv import load_dotenv     #добавил для бота
# load_dotenv()                      #добавил для бота
from config import Config
from forms import SearchForm
from my_elastic import add_to_index, show_res


app = Flask(__name__)
app.config.from_object(Config)


global new_index
global new_index_full
global body
global total


@app.route('/')
def start():
    return render_template('index_search.html')


@app.route('/search',  methods=['GET', 'POST'])
def search():
    global new_index
    global new_index_full
    global body
    global total

    form = SearchForm(request.form)

    if request.method == 'POST':
        name_search = form.name_s.data
        body_search = form.body_s.data
        # new_index = add_to_index('chummy-black-wolfhound.json', name_search)
        fin = []

        s = body_search.splitlines()

        for i in s:
            if ":" in i:
                if i[-1] == ",":
                    i = i[:-1]
                txt = i.split(":")
                for j in txt:
                    if j[0] == ' ':
                        j = j[1:]
                    if j[0] == '"':
                        if j[-1] == '"':
                            j = j[1:-1]
                            if j[0] == ' ':
                                if j[-1] == ' ':
                                    text = j[1:-1]
                                else:
                                    text = j[1:]
                            elif j[-1] == ' ':
                                text = j[:-1]
                            else:
                                text = j
                        else:
                            text = j[1:]
                    elif j[-1] == '"':
                        text = j[:-1]
                    else:
                        if j[0] == ' ':
                            if j[-1] == ' ':
                                text = j[1:-1]
                            text = j[1:]
                        elif j[-1] == ' ':
                            text = j[:-1]
                        else:
                            text = j
                    text.strip(" ")
                    fin.append(text)

        findict = {}
        for i in range(len(fin)):
            if fin[i] == 'text':
                findict[fin[i]] = fin[i + 1]
            elif fin[i] == 'top_k':
                findict[fin[i]] = int(fin[i + 1])
        words = findict['text']
        amount = findict['top_k']
        word_n = {'1': '', '2': ''}
        if words.count(" ") > 0:
            search_words = words.split(" ")
            for i in range(len(search_words)):
                if i == 0:
                    word = search_words[i]
                elif i == 1 and len(search_words) == 2:
                    word_n['1'] = search_words[i]
                    word_n.pop('2')
                elif i == 1:
                    word_n['1'] = search_words[i]
                elif i == 2:
                    word_n['2'] = search_words[i]
        else:
            word = words
            word_n = {}
        if len(word_n) == 2:
            add_q_1 = ',"should": {"match": {"text": "' + word_n['1'] + '"}}'
            add_q_2 = ',"filter": {"match": {"text": "' + word_n['2'] + '"}}'
            main_q = '{"from": 0, "size": ' + str(amount) + ', "query": {"bool": {"must": {"match": {"text": "' + word + '"}}' + add_q_1 + add_q_2 + '}}}'
        elif len(word_n) == 1:
            add_q_1 = ',"should": {"match": {"text": "' + word_n['1'] + '"}}'
            main_q = '{"from": 0, "size": ' + str(amount) + ', "query": {"bool": {"must": {"match": {"text": "' + word + '"}}' + add_q_1 + '}}}'
        else:
            main_q = '{"from": 0, "size": ' + str(amount) + ', "query": {"bool": {"must": {"match": {"text": "' + word + '"}}}}}'
        body_search = main_q
        total = show_res(name_search, body_search)

        string_html = ''
        tbl_o = '<table border = "1px" width = "700px" height = "' + str(len(total) * 100) + 'px">'
        tbl_c = '</table>'
        tr_o = '<tr>'
        tr_c = '</tr>'
        td_o = '<td>'
        td_c = '</td>'
        string_html += tbl_o
        string_html += tr_o + 'Name of index: ' + name_search + tr_o
        string_html += tr_o + td_o + 'score' + td_c + td_o + 'source' + td_c + tr_c
        for i in range(len(total)):
            string_html += tr_o
            for j in range(len(total[i])):
                string_html += td_o
                string_html += str(total[i][j])
                string_html += td_c
            string_html += tr_c
        string_html += tbl_c

        message = Markup(string_html)
        flash(message)
        return redirect(url_for('search'))
    return render_template('search.html', form=form)


#добавил для бота vvvvv

TOKEN = 'hereWILLbeYOURbotTOKEN'
TELEGRAM_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def parse_text(text_msg):
    command_p = [r'@\w+@', r'@\w+\s\w+@', r'@\w+\s\w+\s\w+@']
    message = 'Используйте команды /help и /start'
    if '/' in text_msg:
        if '/start' in text_msg or '/help' in text_msg:
            message = 'Приветствую тебя, мой господин. Твиты Илона Маска к вашим услугам! ' \
                      'Для запроса наберите через пробел слова в формате: \n`@text text@`\n ' \
                      'Например запрос @doge coin@ - будет выдавать твиты со словами "doge" и "coin", которые входят в "топ 10" по значению "score".' \
                      'Максимальное кол-во слов в запросе - три (например @doge home to@).'
            return message
        else:
            return message
    elif '@' in text_msg:
        for i in command_p:
            command = re.search(i, text_msg)
            if command == None:
                continue
            else:
                command = command.group().replace('@', '')
                print(command)
                message = 'Мой господин. Вы запросили Твиты Илона Маска c параметрами:\n' + command + get_total(command)
                break
        if command == None:
            return 'Неверный запрос. Правильный формат: \n`@text text@`\n(максимум три слова)'
        return message
    else:
        return 'Неверный запрос. Используйте /help и /start'

def get_total(command):
    index_name='full_musk'
    words = command
    amount = 10
    word_n = {'1': '', '2': ''}
    if words.count(" ") > 0:
        search_words = words.split(" ")
        for i in range(len(search_words)):
            if i == 0:
                word = search_words[i]
            elif i == 1 and len(search_words) == 2:
                word_n['1'] = search_words[i]
                word_n.pop('2')
            elif i == 1:
                word_n['1'] = search_words[i]
            elif i == 2:
                word_n['2'] = search_words[i]
    else:
        word = words
        word_n = {}
    if len(word_n) == 2:
        add_q_1 = ',"should": {"match": {"text": "' + word_n['1'] + '"}}'
        add_q_2 = ',"filter": {"match": {"text": "' + word_n['2'] + '"}}'
        main_q = '{"from": 0, "size": ' + str(
            amount) + ', "query": {"bool": {"must": {"match": {"text": "' + word + '"}}' + add_q_1 + add_q_2 + '}}}'
    elif len(word_n) == 1:
        add_q_1 = ',"should": {"match": {"text": "' + word_n['1'] + '"}}'
        main_q = '{"from": 0, "size": ' + str(
            amount) + ', "query": {"bool": {"must": {"match": {"text": "' + word + '"}}' + add_q_1 + '}}}'
    else:
        main_q = '{"from": 0, "size": ' + str(
            amount) + ', "query": {"bool": {"must": {"match": {"text": "' + word + '"}}}}}'
    body_search = main_q
    total_bot = show_res(index_name, body_search)
    total_bot_str = ''
    for i in total_bot:
        total_bot_str += '\n----------\n'+str(i)
        message = '\nРезультат:' + total_bot_str
    return message

def send_message(chat_id, msg):
    session = requests.Session()
    r = session.get(TELEGRAM_URL, params=dict(chat_id=chat_id, text=msg, parse_mode='Markdown'))
    return r.json()


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resp = request.get_json()
        print(resp)
        return '<div style="color:green">Привет, это Бот!</div>'
    return '<div style="color:lightblue">Бот тебя услышит...</div>'


class BotAPI(MethodView):

    def get(self):
        return '<div style="color:lightblue">Бот тебя услышит в КЛАССЕ...</div>'

    def post(self):
        resp = request.get_json()
        text_msg = resp['message']['text']
        chat_id = resp['message']['chat']['id']
        tmp = parse_text(text_msg)
        if tmp:
            send_message(chat_id, tmp)
        print(resp)
        return '<div style="color:green">Привет, это КЛАССНЫЙ Бот!</div>'

app.add_url_rule('/TOKEN/', view_func=BotAPI.as_view('bot'))




#добавил для бота ^^^^^


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)