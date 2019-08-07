import cv2 as cv
import numpy as np

class CellTracker(object):
    def ImgSegmentation():
        pass

    def trackKCR():
        pass
    
    def Farnback():
        cap = cv.VideoCapture("C:/Users/alienware/Downloads/color_movie_1.mp4")
        ret, first_frame = cap.read()
        # Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
        first_frame=np.array(first_frame,dtype=np.uint8)
        prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
        mask = np.zeros_like(first_frame)
        mask[..., 1] = 255

        while(cap.isOpened()):

            ret, frame = cap.read()
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, 0.8,1000, 15, 3, 2, 1.6, 0)
            magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])
            mask[..., 0] = angle * 180 / np.pi / 2
            mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)
            rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)
            cv.imshow("dense optical flow", rgb)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv.destroyAllWindows()