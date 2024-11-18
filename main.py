from prediction import prediction
import matplotlib.pyplot as plt
import fire 

def predict_from_teminal(image_path = "img.jpg"):
    annotatedImage = prediction(image_path)
    plt.imshow(annotatedImage)
    plt.grid(False)
    plt.axis('off')
    plt.show()



if __name__=='__main__':
    fire.Fire(predict_from_teminal)
