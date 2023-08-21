#Paste the export txt file from cstimer in the cstimerdata folder, the script will automatically take the top file in the folder.
import os

def get_sessions() -> list: 
    filename = os.listdir(".\cstimerdata")
    with open(f".\cstimerdata\{filename[0]}") as txtfile:
        lines = str(txtfile.readlines()).split("properties")[0].split(":")
        amount_of_sessions = len(lines) - 1
        sessions = []
        for i in range(amount_of_sessions):
            session = lines[i + 1] # session is of type string
            session = string_list_conversion(session)
            sessions.append(get_times(session))
        return sessions

def get_times(session: list[str]):
    timeslist = []
    for solve in session:
        try:
            time = int(solve[0][1])
            if solve[0][0] == -1:
                timeslist.append("DNF")
            elif solve[0][0] != 0:
                timeslist.append(round(time + solve[0][0] / 1000, 2))
            else:
                timeslist.append(round(time / 1000, 2))
        except:
            pass
    return timeslist

def unnested_split(string: str):
    start = 0
    end = None
    returns = []
    netto_bracket = 0
    for i, v in enumerate(string):
        end = i
        if v == "[":
            netto_bracket += 1
        elif v == "]":
            netto_bracket -= 1
        elif (not netto_bracket) and v == ",":
            returns.append(string[start:end])
            start = end + 1
    returns.append(string[start:end+1])
    return returns

def string_list_conversion(string: str, split_string: str = ",") -> list:
    if "[" in string:
        return [string_list_conversion(i) for i in unnested_split(string[1:-1])]
    return string

# I definitely wrote this ^

print(get_sessions())