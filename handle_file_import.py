#Paste the export txt file from cstimer in the cstimerdata folder, the script will automatically take the top file in the folder.
import os

def get_sessions(session_number) -> list: 
    if os.name == "posix":
        filename = os.listdir("./cstimerdata")
        filename = f"./cstimerdata/{filename[0]}"
    else:
        filename = os.listdir(".\cstimerdata")
        filename = f".\cstimerdata\{filename[0]}"

    with open(filename) as txtfile:
        lines = str(txtfile.readlines())
        sessions = lines.split("properties")[0].split('":')
        session = sessions[session_number]
        session: str = session.split("]],")[0] + "]]"
        session_handled = string_list_conversion(session)
        session_name = get_session_name(session_number, lines)
        return get_times(session_handled), session_name

def get_times(session: list):
    timeslist = []
    for solve in session:
        try:
            time = int(solve[0][1])
            if solve[0][0] == "-1":
                timeslist.append(float("nan"))
            elif solve[0][0] != "0":
                timeslist.append(round((time + solve[0][0]) / 1000, 2))
            else:
                timeslist.append(round(time / 1000, 2))
        except:
            pass
    return timeslist

def get_session_name(session_number, lines: str):
    start = lines.index('":"')
    end = lines.rindex('","color"')
    containing_names = lines[start + 3:end]
    dictionary = string_list_conversion(containing_names)
    session_info = dictionary[str(session_number)]
    session_name = session_info["name"]
    return session_name

# -------------------------------------------------------------------------

def parse_dict_element(string: str) -> tuple[object, object]:
    new_string = string.replace(chr(92), "").replace('"', '')
    return new_string[:new_string.index(":")], new_string[new_string.index(":")+ 1:]

def unnested_split_dict(string: str) -> dict:
    start = 0
    end = None
    returns = {}
    netto_sq_bracket = 0
    netto_bracket = 0
    for i, v in enumerate(string):
        end = i
        if v == "{":
            netto_bracket += 1
        elif v == "}":
            netto_bracket -= 1
        elif v == "[":
            netto_sq_bracket += 1
        elif v == "]":
            netto_sq_bracket -= 1
        elif (not netto_bracket) and (not netto_sq_bracket) and v == ",":
            key, value = parse_dict_element(string[start:end])
            returns[key] = value
            start = end + 1
    if string:
        key, value = parse_dict_element(string[start:end+1])
        returns[key] = value
    return returns

def unnested_split_list(string: str) -> list:
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
    if string:
        returns.append(string[start:end+1])
    return returns

def string_list_conversion(string: str) -> list | dict:
    if "{" == string[0]:
        return {k : string_list_conversion(v) for k, v in unnested_split_dict(string[1:-1]).items()}
    if "[" in string:
        return [string_list_conversion(i) for i in unnested_split_list(string[1:-1])]
    return string