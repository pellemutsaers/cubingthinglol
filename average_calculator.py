import math

def calculate_aox(times_list, aox):
    cutoff = math.ceil(aox * 0.05)
    average_list = []
    for i in range(len(times_list)):
        if i >= aox:
            aox_slice = times_list[i+1-aox:i+1]
            aox_slice = sorted(aox_slice, key = lambda x : float('-inf') if math.isnan(x) else x)
            for j in range(cutoff):
                aox_slice[j] = 0
            for k in range(cutoff):
                aox_slice[-(k+1)] = 0
            try:
                average = sum(aox_slice) / (aox - 2*cutoff)
            except:
                average = float("nan")

            average_list.append(average)
    return(average_list)