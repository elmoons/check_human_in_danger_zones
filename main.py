from ultralytics import YOLO


model = YOLO("runs/detect/train5/weights/best.pt")


results = model.train(data="config.yaml", epochs=50,  workers=0)

