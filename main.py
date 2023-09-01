import matplotlib.figure as mpl_figure
import numpy as np
import math
import average_calculator
import handle_file_import
from flask import Flask, render_template, flash, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename
import os

n = 5 # polynomial order
time_list = 0
index_list = []

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)

class Averages():
    def __init__(self, x, color):
        self.x = x
        self.color = color

    def plot(self, ax, thickness_factor):
        aox_list = average_calculator.calculate_aox(time_list, self.x)
        ax.plot(index_list[self.x:], aox_list, linewidth=0.5 * thickness_factor, color=self.color, label=f"ao{self.x}")

def calculate_session(session, file, img="hm.png"):
    global time_list
    global index_list

    time_list = []
    index_list = []

    time_list, name = file.get_sessions(session)
    for i in range(len(time_list)):
        index_list.append(i)

    time_list_copy = time_list.copy()
    index_list_copy = index_list.copy()
    dnf_indices = []

    for index, i in enumerate(time_list_copy):
        if math.isnan(i):
            dnf_indices.append(index)
    dnf_indices.reverse()

    for i in dnf_indices:
        time_list_copy.pop(i)
        index_list_copy.pop(i)

    try:
        regression_values = np.polyfit(index_list_copy, time_list_copy, n)
    except:
        print("session is empty, try another one")
        return 0

    px = np.poly1d(regression_values)
    regression_list = []
    for i in index_list:
        regression_list.append(px(i))

    slowest_time = max(time_list)
    fastest_time = min(time_list)

    thickness_factor = 2.66 - 1.5 * (len(time_list) / 9000)
    if len(time_list) > 10000:
        thickness_factor = 1

    fig = mpl_figure.Figure(facecolor="#dbd8d7")
    ax = fig.add_subplot(1, 1, 1)

    process_singles(ax, slowest_time, fastest_time, thickness_factor)

    averages_to_plot = [5, 12, 50, 100]
    colors = iter(["#f67280", "#c06c84", "#6c5b7b", "#355c7d"])
    for i in averages_to_plot:
        thickness_factor += 0.2
        Averages(i, next(colors)).plot(ax, thickness_factor)


    process_regression(ax, slowest_time, fastest_time, regression_list)

    ax.set_ylim(math.floor(.9*fastest_time), math.ceil(1.1*slowest_time))
    ax.set_xlim(0, len(time_list) * 1.02)
    ax.grid(which="minor", color="grey")
    ax.set_title(name)

    ax.set_facecolor("#dbd8d7")
    ax.spines['left'].set_color('#000000')
    ax.spines['right'].set_color('#000000')
    ax.spines['bottom'].set_color('000000')
    ax.spines['top'].set_color('000000')
    ax.tick_params(axis='x', colors='000000')
    ax.tick_params(axis='y', colors='000000')

    ax.set_xlabel("Solve number")
    ax.set_ylabel("Time in seconds")

    ax.legend(framealpha= 1, loc=1, facecolor="#aba8a7", labelcolor="linecolor", fontsize="large")
    fig.savefig("static/hm.png")

    time_list.sort()
    print(f"Ten best solves from session: {time_list[0:10]}")

def process_regression(ax, slowest_time, fastest_time, regression_list):
    x_margin = 0.005 * len(time_list)
    y_margin = 0.01 * (math.ceil(1.1*slowest_time) - math.floor(.9*fastest_time))

    np_array_regression_list = np.array(regression_list)
    fastest_regression_time = min(np_array_regression_list)
    fastest_regression_time_index = np.argmin(np_array_regression_list)
    fastest_regression_time_fmt = round(fastest_regression_time, 2)

    ax.plot(index_list, regression_list, "--", color="white", linewidth=2, label="Regression line")
    ax.stem(fastest_regression_time_index, fastest_regression_time, markerfmt="k.", linefmt="k-.", orientation="vertical", basefmt=" ", bottom=math.floor(.9*fastest_time))
    ax.text(x_margin, fastest_regression_time - y_margin, f"{fastest_regression_time_fmt}", color="k", horizontalalignment="left", verticalalignment="top")
    ax.text(fastest_regression_time_index + x_margin, math.floor(.9*fastest_time) + y_margin, f"{fastest_regression_time_index}", horizontalalignment="left", verticalalignment="bottom", color="k", rotation="vertical")

def process_singles(ax, slowest_time, fastest_time, thickness_factor):
    x_margin = 0.005 * len(time_list)
    y_margin = 0.01 * (math.ceil(1.1*slowest_time) - math.floor(.9*fastest_time))

    fastest_time_index = np.nanargmin(time_list)

    ax.plot(index_list, time_list, linewidth=0.5 * thickness_factor, color="#f8b195", label="Times")
    ax.stem(fastest_time_index, fastest_time, markerfmt="k.", linefmt="k-.", orientation="vertical", basefmt=" ", bottom=math.floor(.9*fastest_time))
    ax.text(0 + x_margin, fastest_time - y_margin, f"{fastest_time}", color="k", horizontalalignment="left", verticalalignment="top")
    ax.text(fastest_time_index + x_margin, math.floor(.9*fastest_time) + y_margin, f"{fastest_time_index}", horizontalalignment="left", verticalalignment="bottom", color="k", rotation="vertical")

app = Flask(__name__)

# @app.route('/')
# def home():
#     file = handle_file_import.CSTimerDataHandler()

#     session_input = "1"
#     if session_input.isdigit():
#         calculate_session(int(session_input), file)
#     else:
#         return "wtf how ew"
#     return render_template('gay.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        if request.cookies.get('sessionfile') is None:
            return redirect('/upload', 302)
        
        csfile = request.cookies.get('sessionfile')

        file = handle_file_import.CSTimerDataHandler(csfile) #how feed csfile -> ur handle file?

        session_input = "1"
        if session_input.isdigit():
            calculate_session(int(session_input), file)
        else:
            return "wtf how ew"
        return render_template('gay.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Error please submit file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file found')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            resp = make_response(redirect("/", 302))
            resp.set_cookie("sessionfile", file.filename)
            return resp
    else:
        if request.cookies.get('sessionfile') != None:
            return redirect("/", 302)
        return render_template('upload.html')

@app.route('/eatmycookies')
def eatmycookies():
    resp = make_response(redirect('/upload', 302))
    os.remove(f"static/{resp.cookies.get('sessionfile')}")
    resp.delete_cookie('sessionfile')
    return resp

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=False)