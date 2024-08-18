import pickle

file = open('/home/sasha/Documents/vscode/hltv v2 bot/core/model/hltv_v2_model_dump', 'rb')

model = pickle.load(file)

print(type(model))
