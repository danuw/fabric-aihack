The model used here is a YOLOv8 model, trained on the dataset found at: https://universe.roboflow.com/dialog/anpr-mzz7m.

We attempted to train this model in Synapse/Fabric, however we encountered difficulties with both opencv (although resolved) and mlflow. 

The issue with MLFlow was documented on the community forum: https://community.fabric.microsoft.com/t5/Hack-Together/Can-t-disable-MLFlow/m-p/3736570#M169

To re-train the model, follow these steps:
- download the linked training data in YOLO format.
- extract the zip file to the repo directory
- update config.yaml with the relevant model name and path to the data.yaml file in the dataset folder
- Create your venv with the following commands in the terminal:
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
  - `pip install -r requirements.txt`
- run the following to train the model:
  - `python train_model.py`
- Find the new best trained model in the runs folder (runs/model_name{x}/weights/best.pt)
