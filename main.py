from matplotlib import pyplot as plt
# import csv
import numpy as np
import math
import average_calculator
import handle_file_import

n = 5 # polynomial order
time_list = 0
index_list = []

# session_number = 17
# with open(f"CStimer_sessions/session{session_number}.csv") as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=";")
#     csv_reader.__next__()
#     for index, row in enumerate(csv_reader):
#         if "DNF" in row[1]:
#             time_list.append(float("nan"))
#             index_list.append(index)
#         else:
#             if "+" in row[1] and ":" in row[1]:
#                 minute_split = row[1].split(":")
#                 minute_split[1].replace(":", "")
#                 time_list.append(float(minute_split[0])*60 + float(minute_split[1][:-1]) + 2)
#             elif ":" in row[1]:
#                 minute_split = row[1].split(":")
#                 minute_split[1].replace(":", "")
#                 time_list.append(float(minute_split[0])*60 + float(minute_split[1]))
#             elif "+" in row[1]:
#                 time_list.append(float(row[1][:-1]) + 2)

#             else:
#                 time_list.append(float(row[1]))
#             index_list.append(index)
#    calculate_session(time_list)

class Averages():
    def __init__(self, x, color):
        self.x = x
        self.color = color

    def plot(self, thickness_factor):
        aox_list = average_calculator.calculate_aox(time_list, self.x)
        plt.plot(index_list[self.x:], aox_list, linewidth=.5 * thickness_factor, color=self.color, label=f"ao{self.x}")

def calculate_session(session):
    global time_list
    global index_list

    time_list = []
    index_list = []

    time_list, name = handle_file_import.get_sessions(session)
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

    plt.figure(facecolor="#dbd8d7")
    ax = plt.axes()

    process_singles(slowest_time, fastest_time, thickness_factor)

    averages_to_plot = [5, 12, 50, 100]
    colors = iter(["#f67280", "#c06c84", "#6c5b7b", "#355c7d"])
    for i in averages_to_plot:
        thickness_factor += 0.2
        Averages(i, next(colors)).plot(thickness_factor)

    process_regression(slowest_time, fastest_time, regression_list)

    plt.ylim(math.floor(.9*fastest_time), math.ceil(1.1*slowest_time))
    plt.xlim(0, len(time_list) * 1.02)
    plt.grid("minor", color="grey")
    plt.title(name)

    ax.set_facecolor("#dbd8d7")
    ax.spines['left'].set_color('#000000')
    ax.spines['right'].set_color('#000000')
    ax.spines['bottom'].set_color('000000')
    ax.spines['top'].set_color('000000')
    ax.tick_params(axis='x', colors='000000')
    ax.tick_params(axis='y', colors='000000')

    plt.xlabel("Solve number")
    plt.ylabel("Time in seconds")

    plt.legend(framealpha= 1, loc=1, facecolor="#aba8a7", labelcolor = "linecolor", fontsize = "large")
    plt.show()

    time_list.sort()
    print(f"Ten best solves from session: {time_list[0:10]}")

def process_regression(slowest_time, fastest_time, regression_list):
    x_margin = 0.005 * len(time_list)
    y_margin = 0.01 * (math.ceil(1.1*slowest_time) - math.floor(.9*fastest_time))

    np_array_regression_list = np.array(regression_list)
    fastest_regression_time = min(np_array_regression_list)
    fastest_regression_time_index = np.argmin(np_array_regression_list)
    fastest_regression_time_fmt = round(fastest_regression_time, 2)

    plt.plot(index_list, regression_list, "--", color = "white", linewidth=2, label="Regression line")
    plt.stem(fastest_regression_time, fastest_regression_time_index, markerfmt="k.", linefmt="k-.", orientation="horizontal")
    plt.stem(fastest_regression_time_index, fastest_regression_time, markerfmt="k.", linefmt="k-.", orientation="vertical", bottom=math.floor(.9*fastest_time))
    plt.text(x_margin, fastest_regression_time - y_margin, f"{fastest_regression_time_fmt}", color="k", horizontalalignment="left", verticalalignment="top")
    plt.text(fastest_regression_time_index + x_margin, math.floor(.9*fastest_time) + y_margin, f"{fastest_regression_time_index}", horizontalalignment="left", verticalalignment="bottom", color="k", rotation = "vertical")

def process_singles(slowest_time, fastest_time, thickness_factor):
    x_margin = 0.005 * len(time_list)
    y_margin = 0.01 * (math.ceil(1.1*slowest_time) - math.floor(.9*fastest_time))

    fastest_time_index = np.nanargmin(time_list)

    plt.plot(index_list, time_list, linewidth=.5 * thickness_factor, color="#f8b195", label="Times")
    plt.stem(fastest_time, fastest_time_index, markerfmt="k.", linefmt="k-.", orientation="horizontal")
    plt.stem(fastest_time_index, fastest_time, markerfmt="k.", linefmt="k-.", orientation="vertical", bottom=math.floor(.9*fastest_time))
    plt.text(0 + x_margin, fastest_time - y_margin, f"{fastest_time}", color="k", horizontalalignment="left", verticalalignment="top")
    plt.text(fastest_time_index + x_margin, math.floor(.9*fastest_time) + y_margin, f"{fastest_time_index}", horizontalalignment="left", verticalalignment="bottom", color="k", rotation = "vertical")

running = True
while running:
    session_input = input("Type in the number of the session you want to see. For example: 1. To close type enter: ")
    if session_input.isdigit():
        calculate_session(int(session_input))
    else:
        running = False

