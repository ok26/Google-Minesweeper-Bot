import time, keyboard
import numpy as np
from mss import mss
import ctypes

np.set_printoptions(linewidth=100)
gx = 24
gy = 20
revealed = np.zeros((gy,gx))
clicked = np.zeros_like(revealed)
revealed[:,:] = -1
sct = mss()
sq_side = 25
pixel_data = {
   -1 : [[ 88, 215, 124, 255], [ 80, 209, 115, 255]],
    0 : [[140, 187, 205, 255], [144, 187, 239, 255]],
    1 : [[227, 118,   2, 255]],
    2 : [[ 99, 159,  30, 255]],
    3 : [[ 16,  48, 255, 255]],
    4 : [[145,  65, 199, 255]],
    5 : [[  0, 143, 255, 255]],
    6 : [[165, 171, 114, 255]],
    7 : [[ 65,  66,  66, 255]]
}

fin = []

def update_grid():
    sct_image = sct.grab({'top': 354, 'left': 652, 'width': 600, 'height': 500})
    image_np = np.array(sct_image)
    for y in range(gy):
        for x in range(gx):
            sq = image_np[y*sq_side : (y+1)*sq_side, x*sq_side : (x+1)*sq_side]
            v = get_square(sq[9,13])
            if revealed[y,x] != -2:
                revealed[y,x] = v

def get_square(sq):
    cur = -1
    sv = 1e9
    for k,v in pixel_data.items():
        cv = 0
        for i in range(len(v)):
            for j in range(3):
                cv += abs(sq[j] - v[i][j])
            if cv<sv: 
                cur = k
                sv = cv
    return cur
        

def first_empty():
    for y in range(gy):
        for x in range(gx):
            if revealed[y,x]==-1:
                return (x,y)
    return (-1,-1)

def run_algorithm():
    probability = {}
    obvious = []
    for y in range(gy):
        for x in range(gx):
            if (revealed[y,x]>0 and (x,y) not in fin):
                adjacent = []
                bombs = 0
                for i in range(-1,2):
                    for j in range(-1,2):
                        ny = y+i
                        nx = x+j
                        if not (ny==y and nx==x) and 0<=ny<gy and 0<=nx<gx:
                            if (revealed[ny,nx]==-1 and clicked[ny,nx]==0):
                                adjacent.append((nx,ny))
                            elif revealed[ny,nx]==-2:
                                bombs+=1
                if (len(adjacent)==0): 
                    fin.append((x,y))
                    continue

                prob = (revealed[y,x]-bombs) / len(adjacent)
                if prob==1:
                    fin.append((x,y))
                    for square in adjacent:
                        revealed[square[1], square[0]] = -2
                elif prob==0:
                    fin.append((x,y))
                    for sq in adjacent:
                        revealed[sq[1], sq[0]] = 99
                    obvious += adjacent
                else:
                    for square in adjacent:
                        if square in probability and probability[square] >= prob:
                            continue
                        probability[square] = prob
    return (probability, obvious)

def click(x,y):
    ctypes.windll.user32.SetCursorPos(int(x), int(y))
    ctypes.windll.user32.mouse_event(2, 0, 0, 0,0)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0,0)

def run():
    time.sleep(1)
    for sq in [(21,17),(4,17),(11,9)]:
        click(x=sq[0]*sq_side+sq_side/2+652, y=sq[1]*sq_side+sq_side/2+354)
        clicked[sq[1],sq[0]] = 1
    time.sleep(0.67)
    update_grid()
    while True:
        if keyboard.is_pressed('q'): 
            return
        tests = []
        for test in range(4):
            tests.append(run_algorithm())
        obvious = []
        for test in tests: obvious += test[1]
        probability = tests[-1][0]
        if (len(probability)==0 and len(obvious)==0):
            square = first_empty()
            if square==(-1,-1):
                break
            clicked[square[1],square[0]] = 1
            click(x=square[0]*sq_side+sq_side/2+652, y=square[1]*sq_side+sq_side/2+354)
            update_grid()
        elif (len(obvious)==0):
            square = min(probability, key=probability.get)
            clicked[square[1],square[0]] = 1
            click(x=square[0]*sq_side+sq_side/2+652, y=square[1]*sq_side+sq_side/2+354)
            update_grid()
        else:
            for square in obvious:
                if (revealed[square[1], square[0]]==-1 or revealed[square[1], square[0]]==99):
                    clicked[square[1],square[0]] = 1
                    click(x=square[0]*sq_side+sq_side/2+652, y=square[1]*sq_side+sq_side/2+354)
            st = time.time()
            while (time.time()-st<=0.16):
                update_grid()
            

if __name__ == "__main__":
    run()
