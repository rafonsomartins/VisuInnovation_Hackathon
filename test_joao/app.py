from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/delivery', methods=['GET'])
def delivery():
    return render_template("delivery.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)