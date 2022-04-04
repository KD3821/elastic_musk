from flask import Flask, render_template, url_for, redirect, request, flash, Markup
from config import Config
from forms import SearchForm
from my_elastic import add_to_index, show_res


app = Flask(__name__)
app.config.from_object(Config)

global new_index
global body
global total


@app.route('/')
def start():
    return render_template('index_search.html')


@app.route('/search',  methods=['GET', 'POST'])
def search():
    global new_index
    global body
    global total

    form = SearchForm(request.form)

    if request.method == 'POST':
        name_search = form.name_s.data
        body_search = form.body_s.data
        new_index = add_to_index('short-musk.json', name_search)
        total = show_res(name_search, body_search)

        string_html = ''
        tbl_o = '<table border = "1px" width = "700px" height = "' + str(len(total) * 100) + 'px">'
        tbl_c = '</table>'
        tr_o = '<tr>'
        tr_c = '</tr>'
        td_o = '<td>'
        td_c = '</td>'
        string_html += tbl_o
        string_html += tr_o + 'ИМЯ ЗАПРОСА: ' + name_search + tr_o
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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)