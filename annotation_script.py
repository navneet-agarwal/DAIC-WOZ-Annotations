import json
import pandas as pd
import re
import os

if not os.path.exists("./data/annotated_transcripts"):
    os.mkdir("./data/annotated_transcripts")

#  Utility functions

def read_transcript(idx):
    transcript = pd.read_csv(f"./data/transcripts/{idx}_TRANSCRIPT.csv", delimiter='\t')
    return transcript

def remove_brackets(text):
    if type(text) == str:
        text = text.replace("((", "<").replace("))", ">")
        text = re.sub('<.*>', '', text)
        if '(' in text and ')' in text:
            processed = text[text.index('(')+1: text.index(')')]
            return processed
        return text
    elif type(text) == list:
        text_list = [remove_brackets(t) for t in text]
        text_list = [t for t in text_list if len(t)>0]
        return text_list
    return " "

def pre_process_text(transcript):
    values = list(transcript.value)
    speaker = list(transcript.speaker)
    text = "Participant ID: 000\n\n"
    for i in range(len(values)):
        t = speaker[i] + " \t " + remove_brackets(values[i]) + " \n"
        text = text + t
    text = text + "\n\n\nPHQ8 score: 0\nPHQ8 score: 1\nPHQ8 score: 2\nPHQ8 score: 3\n"
    return text

def annotate_text(text, annotations):
    offset = 0
    for temp in annotations['label']:
        text = text[0: temp[0]+offset] + "@@" + text[temp[0]+offset : temp[1]+offset] + "@@" + text[temp[1]+offset : ]
        offset = offset + 4
    return text

def process_annotated_text(idx, annotated_text):
    annotated_text = annotated_text.split("\n\n\n")[0]
    ellie_list = annotated_text.split("Ellie \t")
    if len(ellie_list) == 1:
        values = ellie_list[0].split("Participant \t")[1:]
        speaker = ["Participant" for i in range(len(values))]
    else:
        ellie_list = ellie_list[1:]
        speaker = []
        values = []
        for e in ellie_list:
            speaker.append("Ellie")
            participant_list = e.split("Participant \t")
            values.append(participant_list[0].strip())
            for p in participant_list[1:]:
                speaker.append("Participant")
                values.append(p.strip())
    dict = {'speaker':speaker, 'value':values}
    dataframe = pd.DataFrame.from_dict(dict)
    dataframe.to_csv(f"./data/annotated_transcripts/{idx}_annotated.csv", sep="\t", index=False)

# Loading annotations
with open("./annotations.json") as file:
    lines = file.readlines()
    annotations = json.loads(lines[0])
print(len(annotations))

# Processing transcripts
for ann in annotations:
    # print("Processing transcript id:", ann['id'])
    transcript = read_transcript(ann['id'])
    transcript = transcript.fillna("", inplace=False)
    text = pre_process_text(transcript)
    annotated_text = annotate_text(text, ann)
    process_annotated_text(ann['id'], annotated_text)