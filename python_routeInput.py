import cv2
import PySimpleGUI as sg
import math
from PIL import Image

file = open(r"droneRoute.txt","w")

sg.theme('darkAmber')
butt = [[sg.Button('Forward')],[sg.Button('Left'),sg.Button('Right')], [sg.Button('Backward')]]
turn = [[sg.Button('Finish')],[sg.Button('Rot Left'),sg.Button('Rot Right')]]
check = [[sg.Text("Seat No")], [sg.InputText(key='seatNo')], [sg.Button("Check Seat")]]
layout = [  [sg.Text('Drone Route input')],
            [sg.Text('Input an aerial view'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')],
            [sg.Graph((400,400),(0,0),(400,400),background_color='white',key='graph')],
            [sg.Column(butt),sg.Column(turn), sg.Column(check)]
            ]

lines = list()
spots = list()
img = Image.open(r"drone32.png")
img.save("droneR.png")
# Create the Window
window = sg.Window('Drone route input', layout)
window.Finalize()
graph = window['graph']
seatNo = window['seatNo']
#circle = graph.DrawCircle((20,20), 25,fill_color="black")
drone = graph.DrawImage(location=(200,200),filename="droneR.png")
droneX = 200
droneY = 200
step = 20
rot = 0
# Event Loop to process "events" and get the "values" of the inputs


def toRad(a):
    return (a / 180) * math.pi
def rotate(a):
    if a == 0:
        return
    file = open(r"droneRoute.txt", "a")
    file.write("\nr " + str(a))
    file.close()
    global rot, drone
    rot += a
    rotate_img = img.rotate(rot)
    rotate_img.save("droneR.png")
    graph.Update()
    graph.DeleteFigure(drone)
    drone = graph.DrawImage(location=(droneX, droneY), filename="droneR.png")

def Move(aa,bb):
    if aa == 0 and  bb == 0:
        return
    global droneX,droneY, rot
    a = aa * math.cos(toRad(rot)) - bb * math.sin(toRad(rot))
    b = aa * math.sin(toRad(rot)) + bb * math.cos(toRad(rot))
    file = open(r"droneRoute.txt", "a")
    if aa == 00:
        file.write("\nv " + str(bb))
    else:
        file.write("\nh " + str(aa))
    file.close()
    lines.append(graph.DrawLine((droneX + 16, droneY - 16), (droneX + 16 + a, droneY - 16 + b), width=3))
    droneX += a
    droneY += b
    graph.RelocateFigure(drone, droneX, droneY)

def check(seat):
    lines.append(graph.DrawCircle((droneX + 16, droneY - 16),5))
    file = open(r"droneRoute.txt", "a")
    file.write("\nc " + str(seat))
    file.close()


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    if event == "Forward":
        Move(0,step)
    if event == "Backward":
        Move(0,-step)
    if event == "Right":
        Move(step,0)
    if event == "Left":
        Move(-step,0)
    if event == "Rot Left":
        rotate(45)
    if event == "Rot Right":
        rotate(-45)
    if event == "Check Seat":
        check(seatNo.Get())
    if event == "Finish":
        rotate(-rot)
        Move(200 - droneX,0)
        Move(0, 200-droneY)
        break


#print('You entered ', values[0])


window.close()