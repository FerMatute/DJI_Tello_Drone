from djitellopy import Tello
import cv2
import numpy as np

# Frame source: 0-> from webcam 1-> from drone
frame_source = 0

# Initializing camera stream
if frame_source == 0:
    capture = cv2.VideoCapture(0)
elif frame_source == 1:
    drone = Tello()
    drone.connect()
    drone.streamoff()
    drone.streamon()

# Tamaño de imagen
h = 500
w = 500
area_min = 800

# Valores de HSV para el filtro de color
# HSV initial values
H_min = 70
H_max = 125
S_min = 130
S_max = 200
V_min = 120
V_max = 255
# Create HSV min and max arrays
hsv_min = np.array([H_min, S_min, V_min])
hsv_max = np.array([H_max, S_max, V_max])


def main():
    print("main program running now")
    # Ciclo principal
    while True:
        # Obtaining a new frame
        if frame_source == 0:
            ret, img = capture.read()
            # Create window for sliders
            cv2.namedWindow("Trackbars")
            cv2.resizeWindow("Trackbars", (500, 90))

            # Need to pull from the Windows to get the updated version of the color code
            # Create trackbars for each of the colors (Min)
            cv2.createTrackbar("H_min", "Trackbars", 0, 255, 'create_callback')
            cv2.setTrackbarPos("H_min", "Trackbars", H_min)
            cv2.createTrackbar("S_min", "Trackbars", S_min)
            cv2.setTrackbarPos("S_min", "Trackbars", S_min)
            cv2.createTrackbar("V_min", "Trackbars", V_min)
            cv2.setTrackbarPos("V_min", "Trackbars", V_min)

            # Trackbars for HSV (Max)
            cv2.createTrackbar("Color", "Trackbars", )
            cv2.createTrackbar("Color", "Trackbars", )
            cv2.createTrackbar("Color", "Trackbars", )


        elif frame_source == 1:
            frame_read = drone.get_frame_read()
            img = frame_read.frame
            # Going from RGB to BGR color workspace
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Rotating the image
        img = cv2.flip(img, 1)

        # Resizing the image --- cv2.resize('ImageName',(x_dimension,y_dimension))
        img = cv2.resize(img, (500, 500))
        img_tracking = img.copy()

        # Cambiando al espacio de color HSV
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Aplicar el filtro de color
        mask = cv2.inRange(hsv_img, hsv_min, hsv_max)
        # Sobreponiendo el filtro en la img original
        result = cv2.bitwise_and(img, img, mask=mask)
        # preparar la imagen para obtener los contornos
        imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

        # Getting image contours to find objects
        contours, hierarchy = cv2.findContours(imgGray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            # Find center of the objects if their area is bigger than area_min
            area = cv2.contourArea(cnt)
            if area > area_min:
                # Drawing object contours
                cv2.drawContours(img_tracking, cnt, -1, (255, 0, 255), 7)
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                x, y, w, h = cv2.boundingRect(approx)
                cv2.rectangle(img_tracking, (x, y), (x + w, y + h), (0, 255, 0), 5)
                print(x, y)


        # Writing the battery level in the image cv2.putText(ImageName, text, location, font, scale, color, thickness)
        if frame_source == 1:
            cv2.putText(img, 'Battery:  ' + str(drone.get_battery()), (0, 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0),3)

        # Showing the image in a window
        cv2.imshow("Image", img_tracking)

        # Keyboard monitor
        key = cv2.waitKey(1) & 0xFF

        # close the windows and break the program if 'q' is pressed
        if key == 113:
            cv2.destroyAllWindows()
            if frame_source == 1:
                drone.land()
                drone.streamoff()
                drone.end()
            break


try:
    main()

except KeyboardInterrupt:
    print('KeyboardInterrupt exception is caught')
    cv2.destroyAllWindows()
    if frame_source == 1:
        drone.land()
        drone.streamoff()
        drone.end()

else:
    print('No exceptions are caught')
