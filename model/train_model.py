import os
os.environ['WANDB_DISABLED'] = 'true'
from ultralytics import YOLO
import yaml

model = YOLO('yolov8n.pt')

conf = yaml.load(open('config.yaml', "rb"), Loader=yaml.Loader)

result = model.train(data=conf['data_directory'],
                     device=conf['device'],
                     epochs=conf['epochs'],
                     verbose=conf['verbose'],
                     plots=conf['plots'],
                     save=conf['save'],
                     name=conf['model_name'])

# resulting model is saved in runs/{conf['model_name']}/weights/best.pt