#apologies for spaghetti code
import requests, os
from time import sleep

sleep(10)

#this may be messy, edit these to your heart's content
address = "localhost"
port = "5001"

rep_pen = 1.08
temperature = 0.0
top_p = 0.9
top_k = 0
top_a = 0
typical = 1
tfs = 1
rep_pen_range = 1024
rep_pen_slope = 0.7
sampler_order = [0, 1, 2, 3, 4, 5, 6]
startlen = 50
convolen = 20
max_context_length = 4096
max_length = 1000
stoplist = ["\n", "\n\n", "###"]

prepend = "/".join(os.path.abspath(__file__).split("\\")[:-1])

#def func
def infer_lm(prompt, max_context_length, max_length, rep_pen, temperature, top_p, top_k, top_a,
            typical, tfs, rep_pen_range, rep_pen_slope, sampler_order, stoplist, address="localhost", port="5001"):
    headers = {
	'accept': 'application/json',
	'Content-Type': 'application/json',
    }
    response = requests.get(f'http://{address}:{port}', headers=headers)

    json_data = {"n": 1,
                "max_context_length": max_context_length,
                "max_length": max_length,
                "rep_pen": rep_pen,
                "temperature": temperature,
                "top_p": top_p, "top_k": top_k,
                "top_a": top_a,
                "typical": typical,
                "tfs": tfs,
                "rep_pen_range": rep_pen_range,
                "rep_pen_slope": rep_pen_slope,
                "sampler_order": sampler_order,
                "prompt": prompt,
                "stop_sequence": stoplist}
    response = requests.post(f'http://{address}:{port}/api/latest/generate/', headers=headers, json=json_data)
    response = response.json()['results'][0]['text'].strip()
    return response

while not os.path.isfile(prepend + "/exit.txt"):
    while not os.path.isfile(prepend + "/output.txt"):
        print("...")
        sleep(2)
        if os.path.isfile(prepend + "/exit.txt"):
            exit()

    with open (prepend + "/output.txt", "r", encoding="utf-8") as f:
        loggerr = f.read()

    action = infer_lm(loggerr, max_context_length, max_length, rep_pen, temperature, top_p, top_k, top_a,
            typical, tfs, rep_pen_range, rep_pen_slope, sampler_order, stoplist).strip()

    os.remove(prepend + "/output.txt")

    with open(prepend + "/input.txt", "w", encoding="utf-8") as f:
        f.write(action)

    sleep(2)
