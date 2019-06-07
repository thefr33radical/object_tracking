from numpy import expand_dims
from keras.models import load_model
from keras.preprocessing.image import load_img,img_to_array

def load_img(filename,shape):
    img=load_img(filename)
    width,height=image.size
    image=load_img(filename,target=shape)
    image=img_to_array(image)
    image=image.astype("float32")
    image/=255.0
    image=expand_dims(image,0)
    return image,width,height

def train_yolov3(model_path,file_path,shape):
    model=load_model(model_path)
    image,width,height=load_img(file_path,shape)
    yp=model.predict(image)

    print([a.shape for a in yp])

    

