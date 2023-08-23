
import mysql.connector
mydb=mysql.connector.connect(host='localhost',user='root',passwd='Js181920',database='ngocare')
cursor=mydb.cursor()
import datetime
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

##cursor.execute('create table Resources(NGO_id varchar(100) not NULL, Name_of_NGO varchar(100) not NULL , Resource_name varchar(100), Resources_req int, Resources_ava int, Difference int)')
##cursor.execute('create table Transactions(NGO_id varchar(100) not NUll, Name_of_NGO varchar(100) not NULL, Name_of_Donor varchar(100), Donor_ID varchar(100) not NULL, Item_Donated varchar(100), Amt_or_Quan int, Role varchar(100), Date_of_Donation date)')
##cursor.execute('create table Money(NGO_id varchar(100) PRIMARY KEY, Total_cash int)')

d={}
no_ngo=0
def ngo_signin(): 
    global count 
    global no_ngo
    cursor.execute("select COUNT(DISTINCT(NGO_ID)) from resources") 
    myrecords=cursor.fetchall()
    count=myrecords[0][0]+1 
    id=str(count)+'0'+str(count)
    name=input('Enter your NGO name: ')
    cursor.execute("insert into money values('"+id+"','"+str(no_ngo)+"')")
    mydb.commit()
    while True: 
        resource_name=input('Enter the resource name: ')
        resource_req=int(input('Enter quantity of resources required(in kg): '))
        resource_ava=int(input('Enter any pre acquired stock if present or enter 0(in kg): '))
        x=resource_req-resource_ava 
        new=input('To enter a new resource press any character of press * to stop: ')
        cursor.execute("insert into resources values('"+id+"','"+name+"','"+resource_name+"','"+str(resource_req)+"','"+str(resource_ava)+"','"+str(x)+"')")
        mydb.commit()
        if new == '*':
            print('Thank you, your profile has been updated!!')
            print("Your NGO ID is", id) 
            break

def ngo_view(ngoid): 
    print("\nHere is a table of your resources:\n")
    cursor.execute("select Resource_name, Resources_req, Resources_ava, Difference from RESOURCES where ngo_id='"+ngoid+"'")
    x=cursor.fetchall()
    df = pd.DataFrame(x,columns = ['Resource Name','Amt required','Amt avalaible','Difference'])
    print (df)


def ngo_insert(ngoid): #to add a new resource for pre-existing ngo
    cursor.execute("select Ngo_id, Name_of_NGO from Resources where ngo_id='"+ngoid+"'")
    myrecords=cursor.fetchall()
    while True: 
        res_name=input('\nEnter new resource: ')
        res_req=int(input('Enter quantity of resources required(in kg): '))
        res_ava=int(input('Enter any pre acquired stock if present or enter 0(in kg): '))
        x=res_req-res_ava
        new=input('To enter a new resource press any character of press * to stop: ')
        cursor.execute("insert into resources values('"+myrecords[0][0]+"','"+myrecords[0][1]+"','"+res_name+"','"+str(res_req)+"','"+str(res_ava)+"','"+str(x)+"')")
        mydb.commit()
        if new == '*':
                print('Thank you, your profile has been updated!!')
                break

def ngo_del(ngoid): #to delete any pre-existing resource
        ngo_view(ngoid) 
        res_name=input('Enter resource name to be deleted: ')
        y=res_name.lower()
        cursor.execute("DELETE FROM resources WHERE Resource_name = '"+y+"'")
        mydb.commit()
        print('Thank you, your profile has been updated!!')
    
def donor_view(): #to view all ngos and the resources available 
    cursor.execute("select NGO_id,Name_of_NGO, Resource_name, Resources_req from RESOURCES ORDER BY ngo_id")
    myrecords=cursor.fetchall()
    c=0
    for x in myrecords: #creating dict
        d[c]=x
        c+=1
    y=0
    df = pd.DataFrame(myrecords,columns = ['Ngo_id','Name of ngo','Resource Name','Amt required'])
    print (df)

def donor_signin(): #to register donors
    flag=int(input('Press 1 if you have donated before or press 2: '))
    if flag == 1:
        id=input('Enter your donor id: ')
    else:
        cursor.execute("select COUNT(DISTINCT(donor_ID)) from transactions")
        myrecords=cursor.fetchall()
        count1=myrecords[0][0]+1
        id=str(count1)+'00'+str(count1)
    name=input('Enter your name: ')
    while True:
        donor_view()
        ngo=int(input("\nEnter the number of the NGO you want to donate to: "))
        qua=int(input('Enter amount of resources donated: '))
        cursor.execute("select COUNT(DISTINCT(donor_ID)) from transactions")
        myrecords=cursor.fetchall()
        for i in d.keys():
            if ngo==i:
                cursor.execute("insert into transactions values('"+d[i][0]+"','"+d[i][1]+"','"+name+"','"+id+"','"+d[i][2]+"','"+str(qua)+"','"+'NULL'+"','"+str(datetime.datetime.now())+"')") 
                mydb.commit()
                if d[i][2].lower() == 'money': #if donor donates money
                    cursor.execute("update money set total_cash = total_cash + "+str(qua)+" where ngo_id ="+d[i][0])
                    mydb.commit()
                    cursor.execute("update resources set Resources_req = Resources_req - "+str(qua)+" where Resource_name='"+d[i][2]+"' and ngo_id ="+d[i][0])
                    mydb.commit()
                    cursor.execute("update resources set Resources_ava = Resources_ava + "+str(qua)+" where Resource_name='"+d[i][2]+"' and ngo_id ="+d[i][0])
                    mydb.commit()
                    cursor.execute("update resources set difference = Resources_req - Resources_ava where Resource_name='"+d[i][2]+"' and ngo_id ="+d[i][0])
                    mydb.commit()
                else: #if donor chooses a resource
                    cursor.execute("update resources set Resources_req = Resources_req - "+str(qua)+" where Resource_name='"+d[i][2]+"' and ngo_id ="+d[i][0])
                    mydb.commit()
                    cursor.execute("update resources set Resources_ava = Resources_ava + "+str(qua)+" where Resource_name='"+d[i][2]+"' and ngo_id ="+d[i][0])
                    mydb.commit()
                    cursor.execute("update resources set difference = Resources_req - Resources_ava where Resource_name='"+d[i][2]+"' and ngo_id ="+d[i][0])
                    mydb.commit()
        new=input('To donate again press any character of press * to stop: ')       
        if new == '*':
            print('Thank you, your profile has been updated!!')
            print("Your donor ID is", id)
            donor_receipt(id) #printing receipt
            break

def donor_receipt(x):
    DATA = [
	[ "Date of donation","ID", "Name", "NGO name", "Item donated","Amt Donated" ],
    ]
    y=datetime.date.today() #getting today's date
    cursor.execute("select Date_of_Donation,Donor_ID,Name_of_Donor,Name_of_NGO,Item_Donated,Amt_or_Quan from TRANSACTIONS where Donor_id="+x)
    myrecords=cursor.fetchall()
    for i in myrecords:
        flag=[]
        if i[0]==y:
            for j in i:
                flag.append(j)
        DATA.append(flag)
    pdf=SimpleDocTemplate("receipt.pdf", pagesize=letter) 
    styles=getSampleStyleSheet()
    title_style=styles["Heading1"]
    title_style.alignment=1
    title=Paragraph("Ngocare", title_style)
    style=TableStyle(
	[
		("BOX", (0, 0), (-1, -1), 1, colors.black), #'1' - thickness of box
		("GRID", (0, 0), (6, 6), 1, colors.black), #(6,6) - number of rows & columns
		("BACKGROUND", (0, 0), (5, 0), colors.darkblue), #(5,0) - size of pdf
		("TEXTCOLOR", (0, 0), (-1, -1), colors.whitesmoke),
		("ALIGN", (0, 0), (-1, -1), "CENTER"),
		("BACKGROUND", (0, 1), (-1, -1), colors.lightblue),
	]
    )
    table=Table(DATA, style=style)
    pdf.build([title, table])

print("Welcome to NGOCare, a platform to connect numerous NGOs with donors!\n")
print('''1 - If you are an NGO
2 - If you want to donate
0 - If you want to exit\n''')
choice=int(input('Enter your choice: '))
while choice!=0:
    if choice == 1: #NGO
        print("\n1 - If you are here for the first time")
        print("2 - If you are already registered\n")
        choice2=int(input('Enter your choice: '))
        if choice2==1:
            ngo_signin()
        elif choice2==2: 
            ngoid=str(input("Enter the ID of your NGO: "))
            print("\n1 - If you want to add a new resource")
            print("2 - If you want to delete a resource")
            print("3 - If you want to view the pre-existing resources")
            print("0 - If you want to exit\n")
            choice3=int(input('Enter your choice: '))
            while choice3!=0:
                if choice3==1:
                    ngo_view(ngoid)
                    ngo_insert(ngoid)
                elif choice3==2:
                    ngo_del(ngoid)
                elif choice3==3:
                    ngo_view(ngoid)
                else:
                    print('Please enter a valid choice\n')
                print("\n1 - If you want to add a new resource")
                print("2 - If you want to delete a resource")
                print("3 - If you want to view the pre-existing resources")
                print("0 - If you want to exit\n")
                choice3=int(input('Enter your choice: '))
        else:
            continue
    elif choice == 2: #DONOR
        donor_signin()
    else:
        print('Please enter a valid choice\n')
    print('''\n1 - If you are an NGO
2 - If you want to donate
0 - If you want to exit\n''')
    choice=int(input('Enter your choice: '))

    
        
