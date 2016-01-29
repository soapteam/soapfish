from flask import Flask
from stock.gen import SERVICE, SERVICE11, SERVICE12

from soapfish.flask_ import flask_dispatcher

ws_ops = flask_dispatcher(SERVICE)
dispatch11 = flask_dispatcher(SERVICE11)
dispatch12 = flask_dispatcher(SERVICE12)

app = Flask(__name__)

app.add_url_rule('/ws/ops', 'ws_ops', ws_ops, methods=['GET', 'POST'])
app.add_url_rule('/stock/soap11', 'dispatch11', dispatch11,
                 methods=['GET', 'POST'])
app.add_url_rule('/stock/soap12', 'dispatch12', dispatch12,
                 methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(debug=True)
