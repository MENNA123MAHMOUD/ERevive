from removeLines import scale_contours
import numpy as np
import cv2

def detectWeakHelper(img):
    h,w = img.shape
    countStartZerosVer = []
    img = cv2.copyMakeBorder(img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, None, value = 255)
    #vertical
    for j in range(w+10):
        countCol=0
        for i in range(h-1):
            if(img[i,j]==255 and img[i+1,j]==0):
                countCol+=1
        countStartZerosVer.append(countCol)

    countAllVer = sum([1 for i in countStartZerosVer if i >=3])
    return countAllVer/len(countStartZerosVer)

def detectWeak(img,contours,shapes):
    bin_img = (img >180)*255
    bin_img = bin_img.astype(np.uint8)
    isWeak = []
    i=0
    hImg,wImg = img.shape
    for c,s in zip(contours,shapes):
        x,y,w,h = cv2.boundingRect(c)
        w = min(x+w+10,wImg)
        h = min(y+h+10,hImg)
        x = max(0,x-10)
        y = max(0,y-10)

        c_small = scale_contours([c.copy()],0.7)
        cv2.drawContours(bin_img,c_small,-1,255,-1)
        imgContour = bin_img[y:h,x:w]
        #cv2.imwrite('bin_img'+str(i)+'.png',imgContour)
        # if i==5:
        #     print("is weak  ",detectWeakHelper(imgContour))
        # i+=1
        

        isWeak.append(detectWeakHelper(imgContour) >= 0.45)
        
    return isWeak