import os
import cv2
import MySQLdb
from tkinter import *
from tkinter import messagebox, filedialog, ttk
import shutil
import numpy as np
import faceRecognition as fr
from PIL import Image, ImageTk
import sys
import random
import time

def logout():
        root.destroy()
        loginscreen()
        
def checkLogin():
        global userId
        global unameDis
        u = nameE.get()
        p = pwordE.get()
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        cur.execute("SELECT * FROM login_tbl where username='" + u + "' and password='"+p+"'")
        flag=0
        for row in cur.fetchall():
                if row[2] == p:
                        flag=1
                        userId=row[0]
                        unameDis=row[3]
                        break
        if flag == 1:
                #messagebox.showinfo('Login', 'Login Succesful')
                root.destroy()
                mainScreen()
        else:
                messagebox.showinfo('Login', 'Incorrect Username or Password')
                nameE.delete(0, END)
                pwordE.delete(0, END)

def userRegister():
        global ids
        usersname=uname.get()
        passwords=password.get()
        usernames=username.get()
        emails=email.get()
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        sql = "INSERT INTO login_tbl(uid,username,password,name,email,status)VALUES (null,'"+usernames+"','"+passwords+"','"+usersname+"','"+emails+"','1')"
        try:
                cur.execute(sql)
                db.commit()
                ids=cur.lastrowid
                messagebox.showinfo('Login', 'User Successfully Registered.')
                uploadCall()
                #uname.delete(0, END)
                #username.delete(0, END)
                #password.delete(0, END)
                #email.delete(0, END)
                #print(ids)
        except pymysql.Error:
                db.rollback()
def uploadCall():
        root.destroy()
        uploadReg()
        
                

def uploadTrainingImg():
        global filepaths
        idss=ids
        filepaths=filedialog.askopenfilename()
        directory = os.path.split(filepaths)[0]
        print(directory)
        #dest='dest'
        #newpath = "dest/1"
        newpath = "dest/"+str(idss)
        os.makedirs(newpath)
        dest="dest/"+str(idss)
        src_files = os.listdir(directory)
        for file_name in src_files:
                full_file_name = os.path.join(directory, file_name)
                if (os.path.isfile(full_file_name)):
                        shutil.copy(full_file_name, dest)
        messagebox.showinfo('Image Upload', 'Photo uploaded')
        uploadComplete()
def uploadComplete():
        root.destroy()
        loginscreen()
        
        

def registerscreen():
        global uname
        global password
        global username
        global email
        global root
        root = Tk()
        root.title('User Register')
        root.geometry('600x300+500+250')
        ins = Label(root, text='Enter Registration Details')
        ins.grid(sticky=W)
        uname1 = Label(root, text='Name')
        username1 = Label(root, text='Username')
        password1 = Label(root,text='Password')
        email1= Label(root,text='Email')
        uname1.grid(row=1, sticky=W)
        username1.grid(row=2, sticky=W)
        password1.grid(row=3, sticky=W)
        email1.grid(row=4, sticky=W)
        uname = Entry(root)
        username = Entry(root)
        password = Entry(root, show='*')
        email = Entry(root)
        uname.grid(row=1, column=1)
        username.grid(row=2, column=1)
        password.grid(row=3, column=1)
        email.grid(row=4, column=1)
        uname.focus()
        loginB = Button(root, text='Register', command=userRegister)
        loginB.grid(columnspan=2)
        
def uploadReg():
        global root
        root = Tk()
        root.title('Upload Photo')
        root.geometry('600x300+500+250')
        ins = Label(root, text='Choose the file to upload:')
        ins.grid(sticky=W)
        loginu = Button(root, text='Upload Images', command=uploadTrainingImg)
        loginu.grid(columnspan=7)
        
        
        

def new_register():
        root.destroy()
        registerscreen()

def detect_faces(f_cascade, color_img, scaleFactor=1.1):
	img_copy = color_img.copy()

	gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)

	faces = f_cascade.detectMultiScale(gray, scaleFactor = scaleFactor, minNeighbors=10)

	for (x,y,w,h) in faces:
		cv2.rectangle(img_copy, (x,y), (x+w,y+h), (0,255,0), 2)

	return img_copy
def find_face(imageNames):
        haar_file = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
        test_img = cv2.imread("dest_folder/"+imageNames)
        test_img = cv2.resize(test_img, (2000,2000))
        test_img = detect_faces(haar_file,test_img)
        #cv2.imshow("bikas",test_img)
        #name={0:"Bikas",1:"Bishal"}
        name={}
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        cur.execute("SELECT * FROM login_tbl")
        for row in cur.fetchall():
                #imageName=row[2]
                uidd=int(row[0])
                uidd=uidd-1
                name.update({uidd:row[3]})
        faces_detected,gray_img=fr.faceDetection(test_img)
        print("faces_detected:",faces_detected)
        face_recognizer=cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.read('trainingData.yml')
        for face in faces_detected:
                (x,y,w,h)=face
                roi_gray=gray_img[y:y+h,x:x+h]
                label,confidence=face_recognizer.predict(roi_gray)#predicting the label of given image
                print("confidence:",confidence)
                print("label:",label)
                fr.draw_rect(test_img,face)
                predicted_name=name[label]
                uidds=label+1
                if(userId !=uidds):
                        if(confidence>47):#If confidence less than 37 then don't print predicted face text on screen
                                continue
                        db = MySQLdb.connect('localhost', 'root','','facetag_db')
                        cur = db.cursor()
                        sql = "INSERT INTO tagimg_tbl(id,img_id,uid,date,status)VALUES (null,'"+str(image_ids)+"','"+str(label+1)+"', '2020-04-10','0')"
                        try:
                                cur.execute(sql)
                                db.commit()
                        except pymysql.Error:
                                db.rollback()
                fr.put_text(test_img,predicted_name,x,y)
        resized_img=cv2.resize(test_img,(700,700))
        cv2.imshow("face detection",resized_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
             
def callback():
        global filepath
        global image_ids
        imageName=0
        filepath=filedialog.askopenfilename()
        dest='dest_folder'
        img_name=os.path.basename(filepath)
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        cur.execute("SELECT * FROM image_tbl")
        for row in cur.fetchall():
                imageName=row[2]
        imageName=int(imageName)     
        imageName=imageName+1
        print("image name=")
        print(imageName)
        shutil.copy(filepath,dest)
        os.rename("dest_folder/"+img_name,"dest_folder/"+str(imageName)+".jpg")
        imageNames=str(imageName)+".jpg"
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        sql = "INSERT INTO image_tbl(img_id,uid,name,status)VALUES (null,'"+str(userId)+"','"+str(imageName)+"','1')"
        try:
                cur.execute(sql)
                db.commit()
                image_ids=cur.lastrowid
                find_face(imageNames)
        except pymysql.Error:
                db.rollback()
def tests():
        global myvar
        images = []

        images.append('dest_folder/1.jpg')
        images.append('dest_folder/2.jpg')
        images.append('dest_folder/3.jpg')
        images.append('dest_folder/4.jpg')




        ## Main window
        root = Tk()
        ## Grid sizing behavior in window
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        ## Canvas
        cnv = Canvas(root)
        cnv.grid(row=0, column=0, sticky='nswe')
        ## Scrollbars for canvas
        hScroll = Scrollbar(root, orient=HORIZONTAL, command=cnv.xview)
        hScroll.grid(row=1, column=0, sticky='we')
        vScroll = Scrollbar(root, orient=VERTICAL, command=cnv.yview)
        vScroll.grid(row=0, column=1, sticky='ns')
        cnv.configure(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)
        ## Frame in canvas
        frm = Frame(cnv)
        ## This puts the frame in the canvas's scrollable zone
        cnv.create_window(0, 0, window=frm, anchor='nw')
        ## Frame contents
        #selection
        for s in images:
                print(s)
                #im = Image.open(s)
                #im = im.resize((500,500))
                #tkimage = ImageTk.PhotoImage(im)
                #myvar=Label(root,image = tkimage)
                #myvar.image = tkimage
                #myvar.grid()
        ## Update display to get correct dimensions
        frm.update_idletasks()
        ## Configure size of canvas's scrollable zone
        cnv.configure(scrollregion=(0, 0, frm.winfo_width(), frm.winfo_height()))
        ## Go!
        root.mainloop()

        
def test():
        im = Image.open('dest_folder/1.jpg')
        tkimage = ImageTk.PhotoImage(im)
        myvar=Label(root,image = tkimage)
        myvar.image = tkimage
        myvar.grid()
def openmain():
        root.destroy()
        mainScreen()

def viewuploadPhoto():
        global root
        global myvar
        #tests()
        #root = Tk()
        #root.geometry('600x600+500+250')
        images = []
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        cur.execute("SELECT * FROM image_tbl where uid='"+str(userId)+"'")
        for row in cur.fetchall():
                print(row[2])
                Imgname="dest_folder/"+str(row[2])+".jpg"
                images.append(Imgname)
                #imgs= cv2.imread("dest_folder/"+Imgname)
                #cv2.imshow("face dtecetion",imgs)
        ## Main window
        root = Tk()
        root.title('View Uploaded Photo')
        ## Grid sizing behavior in window
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        ## Canvas
        cnv = Canvas(root)
        cnv.grid(row=0, column=0, sticky='nswe')
        ## Scrollbars for canvas
        hScroll = Scrollbar(root, orient=HORIZONTAL, command=cnv.xview)
        hScroll.grid(row=1, column=0, sticky='we')
        vScroll = Scrollbar(root, orient=VERTICAL, command=cnv.yview)
        vScroll.grid(row=0, column=1, sticky='ns')
        cnv.configure(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)
        ## Frame in canvas
        frm = Frame(cnv)
        ## This puts the frame in the canvas's scrollable zone
        cnv.create_window(0, 0, window=frm, anchor='nw')
        ## Frame contents
        #selection
        ax = []
        win = Toplevel()
        r=10
        c=20
        for s in images:
                print(s)
                im = Image.open(s)
                im = im.resize((500,500))
                tkimage = ImageTk.PhotoImage(im)
                myvar=Label(frm,image=tkimage)
                myvar.image = tkimage
                myvar.grid()
        Button(frm,text="GO BACK",command=openmain).grid()
        ## Update display to get correct dimensions
        frm.update_idletasks()
        ## Configure size of canvas's scrollable zone
        cnv.configure(scrollregion=(0, 0, frm.winfo_width(), frm.winfo_height()))
        ## Go!
        root.mainloop()
def viewPhotos():
        root.destroy()
        viewuploadPhoto()
        
        
def taggedPhoto():
        global root
        global myvar
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        #print (userId)
        tagimages = []
        uploaderName=[]
        cur.execute("SELECT * FROM tagimg_tbl where uid='"+str(userId)+"'")
        for row in cur.fetchall():
                cur.execute("SELECT * FROM image_tbl where img_id='"+str(row[1])+"'")
                for rows in cur.fetchall():
                        cur.execute("SELECT * FROM login_tbl where uid='"+str(rows[1])+"'")
                        for rowss in cur.fetchall():
                                #print (rowss[3])
                                uploaderName.append(rowss[3])
                        #print(rows[2])        
                        Imgname=str(rows[2])+".jpg"
                        Imgname3="dest_folder/"+str(rows[2])+".jpg"
                        tagimages.append(Imgname3)
                        imgs= cv2.imread("dest_folder/"+Imgname)
                        #cv2.imshow("face dtecetion",imgs)
        ## Main window
        root = Tk()
        root.title('Tagged Photos')
        ## Grid sizing behavior in window
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        ## Canvas
        cnv = Canvas(root)
        cnv.grid(row=0, column=0, sticky='nswe')
        ## Scrollbars for canvas
        hScroll = Scrollbar(root, orient=HORIZONTAL, command=cnv.xview)
        hScroll.grid(row=1, column=0, sticky='we')
        vScroll = Scrollbar(root, orient=VERTICAL, command=cnv.yview)
        vScroll.grid(row=0, column=1, sticky='ns')
        cnv.configure(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)
        ## Frame in canvas
        frm = Frame(cnv)
        ## This puts the frame in the canvas's scrollable zone
        cnv.create_window(0, 0, window=frm, anchor='nw')
        i=0
        for s in tagimages:
                #print(s)
                im = Image.open(s)
                im = im.resize((500,500))
                tkimage = ImageTk.PhotoImage(im)
                myvar=Label(frm,image=tkimage)
                myvar.image = tkimage
                myvar1=Label(frm,text="Uploaded By:"+uploaderName[i])
                i=i+1
                myvar.grid()
                myvar1.grid()
        Button(frm,text="GO BACK",command=openmain).grid()        
        ## Update display to get correct dimensions
        frm.update_idletasks()
        ## Configure size of canvas's scrollable zone
        cnv.configure(scrollregion=(0, 0, frm.winfo_width(), frm.winfo_height()))
        ## Go!
        root.mainloop()
def tagphoto():
        root.destroy()
        taggedPhoto()
def notification():
        global root
        global myvar
        db = MySQLdb.connect('localhost', 'root','','facetag_db')
        cur = db.cursor()
        print (userId)
        notifi_user = []
        cur.execute("SELECT * FROM tagimg_tbl where uid='"+str(userId)+"'")
        for row in cur.fetchall():
                cur.execute("SELECT * FROM image_tbl where img_id='"+str(row[1])+"'")
                for rows in cur.fetchall():
                        cur.execute("SELECT * FROM login_tbl where uid='"+str(rows[1])+"'")
                        for rowss in cur.fetchall():
                                notifi_user.append(rowss[3])
                                #print(rowss[3])        
                        #Imgname=str(rows[2])+".jpg"
                        #Imgname3="dest_folder/"+str(rows[2])+".jpg"
                        #tagimages.append(Imgname3)
                        #imgs= cv2.imread("dest_folder/"+Imgname)
                        #cv2.imshow("face dtecetion",imgs)
        root = Tk()
        root.title('Notification')
        root.geometry('600x300+500+250')
        i=1
        username1 = Label(root, text="You Are Tagged by:")
        username1.grid(row=i, sticky=W)
        for name in notifi_user:
                i=i+1
                username1 = Label(root, text=name)
                username1.grid(row=i, sticky=W)
        Button(root,text="GO BACK",command=openmain).grid()        
                
        
        
def tagNotify():
        root.destroy()
        notification()
        
def mainScreen():
        global root
        root = Tk()
        print(userId) 
        root.title('Main Page')
        root.geometry('800x500+500+250')
        Label(root,font=100,text="Face Detection Tagging System").grid(row=0,column=50,sticky=W)
        Label(root,text="Welcome ").grid(row=2,column=5,sticky=W)
        Label(root,text=unameDis).grid(row=2,column=20,sticky=W)
        Button(root,text="Notification",command=tagNotify).grid(row=10, column=30,sticky=W)
        Button(root,text="Upload Photo",command=callback).grid(row=10, column=40,sticky=W)
        Button(root,text="View Photos",command=viewPhotos).grid(row=10, column=50,sticky=W)
        Button(root,text="Tagged Photos",command=tagphoto).grid(row=10, column=60,sticky=E)
        Button(root,text="LogOut",command=logout).grid(row=10, column=70,sticky=W)
        root.mainloop()

def loginscreen():
	global nameE
	global pwordE
	global root
	root = Tk()
	root.title('Login')
	root.geometry('300x150+500+250')
	ins = Label(root, text='Enter Login Details')
	ins.grid(sticky=W)

	name = Label(root, text='Username')
	pword = Label(root, text='Password')
	name.grid(row=1, sticky=W)
	pword.grid(row=2, sticky=W)

	nameE = Entry(root)
	pwordE = Entry(root, show='*')
	nameE.grid(row=1, column=1)
	pwordE.grid(row=2, column=1)
	nameE.focus()

	loginB = Button(root, text='Login', command=checkLogin)
	loginB.grid(columnspan=2)
	Button(root,text="New Register",command=new_register).grid()
	root.mainloop()

loginscreen()	
