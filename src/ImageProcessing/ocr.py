import pytesseract
import cv2
import numpy as np
import skimage.io as io
import os
import re

#################### Detect Keys ######################################
def keyDetection(image):
    
    ######### getting all contours in image ###############
    contours , _ = cv2.findContours(image , cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  

    ########### detect contour of line #############

    bottom = 0
    lineIndex = 0
    index = 0
    keyFound = False

    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        
        if y > image.shape[0]//2 and w > image.shape[1]//4 and h < image.shape[0]//4:
            lineIndex = index
            keyFound = True
        index+=1

    ############# delete contour of line #############
    if keyFound == True:
        x,y,w,h = cv2.boundingRect(contours[lineIndex])
        image[y:y+h,x:x+w] = 255
    return keyFound,image


#################### Reading text files ###############################
def OCR():
    os.chdir('./output')
    #print(os.getcwd())
    textArr = []
    numFiles = 0
    isKey = []
    keyFound = False

    for count, f in enumerate(os.listdir()):
        f_name, f_ext = os.path.splitext(f)
        if (f_name[0:4] == "text") and (int(f_name[4:]) > numFiles):
            numFiles = int(f_name[4:])

    for i in range (numFiles+1):
            image = cv2.imread("./text" + str(i) + ".png")
            image = 255 - image

            greyImage = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            threshold , binarizedImage = cv2.threshold(greyImage , 150 , 255 , cv2.THRESH_BINARY)

            outImg = np.ones((image.shape),np.uint8)
            keyFound,outImg = keyDetection(binarizedImage)
            isKey.append(keyFound)

            cv2.imwrite("/home/hager/college/GP/GP/src/ImageProcessing/connectEntitiesOutput/yaaaaay"+str(i)+".png",outImg)
            custom_config = r'--oem 3 --psm 6'
            extractedText = pytesseract.image_to_string(outImg,config=custom_config)
            #print(extractedText)
            if extractedText == "\x0c":
                extractedText = ""
            else:
                extractedText = extractedText.split('\n')[0]

            #remove special char from text
            extractedText = re.sub('[^a-zA-Z0-9 \n\-_]', '', extractedText)
            extractedText = extractedText.replace(" ","_")
            textArr.append(extractedText)
            
    return textArr,isKey

def addDefaultNames(shapes,textArr,dataTypesArr):
    entityCounter, relationCounter, attrCounter = 1,1 ,1

    for i in range(len(shapes)):
        if not textArr[i]:
            if shapes[i] == "rectangle":
                textArr[i] = "entity_" + str(entityCounter)
                entityCounter += 1
            elif shapes[i] == "diamond":
                textArr[i] = "relation_" + str(relationCounter)
                relationCounter += 1
            else:
                textArr[i] = "attr_" + str(attrCounter)
                attrCounter += 1
            dataTypesArr[i] = "str"
        elif textArr[i][-1] == "#":
            textArr[i] = textArr[i][:-1]
    
    return textArr , dataTypesArr
                

