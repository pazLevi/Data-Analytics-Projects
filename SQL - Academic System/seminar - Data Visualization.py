import matplotlib.pyplot as plt
import seaborn as sns
from enum import Enum,auto
from tkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
import tkinter
from tkcalendar import Calendar
import time
from pandastable import Table, TableModel
import pandas as pd
import numpy as np
import time
from tkinter.filedialog import askopenfile
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy as np
from urllib.request import urlopen


class Model:
    search_list = ['Students','Lecturers','Courses','Take']
    queries_list = ['Show the best student',
                    'Show students older then',
                    'Show number of failed students per course',
                    'Show a table of average grade per course',
                    'Show a table of average grade per student',
                    'Show information of student by ID',
                    'Show a table of the students of the most senior lecturer',
                    'Show the weekly hours for every student',
                    'Show the students that study more than X NAZ',
                    'Show avarage by school']
    def __init__(self):
        self.students = pd.read_csv('Students.csv')
        self.students = self.students.set_index(self.students.columns[0],drop=True)
        self.lecturers = pd.read_csv('Lecturers.csv')
        self.lecturers = self.lecturers.set_index(self.lecturers.columns[0],drop=True)
        self.courses = pd.read_csv('Courses.csv')
        self.courses = self.courses.set_index(self.courses.columns[0],drop=True)
        self.take = pd.read_csv('Take.csv')

    class Type(Enum):
        STUDENTS = 0
        COURSES = 1
        LECRURER = 2
        TAKE = 3


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.input = None
        self.query_val = None
    def build_q(self):
        if Model.queries_list[0] == self.query_val:
            best_student = self.model.students.loc[self.model.take.groupby("Student ID").mean()[self.model.take.groupby("Student ID").mean()['Grade'] == self.model.take.groupby("Student ID").mean()['Grade'].max()].Grade.index ]
            best_student['Grade'] = self.model.take.groupby("Student ID").mean().max().Grade
            self.df = best_student
            
        elif(Model.queries_list[1] == self.query_val):
            self.df = self.model.students[self.model.students['Age'] > self.input]

        elif(Model.queries_list[2] == self.query_val):
            failed = self.model.courses.loc[self.model.take[self.model.take.Grade < 60].groupby('Course ID').count().index]
            failed["Failed students"] = self.model.take[self.model.take.Grade < 60].groupby('Course ID').count()['Student ID']
            self.df = failed[['Name','Failed students']]   
                    
        elif(Model.queries_list[3] == self.query_val):
            self.df = self.model.courses.join(self.model.take.groupby('Course ID').mean().Grade)[['Name', 'NAZ', 'Grade']]
            
        elif(Model.queries_list[4] == self.query_val):
            self.df = self.model.students.join(self.model.take.groupby('Student ID').mean().Grade)
        
        elif(Model.queries_list[5] == self.query_val):
            if self.input in self.model.students.index:
                self.df = pd.DataFrame(self.model.students.loc[self.input])
            else: 
                self.df = pd.DataFrame()
        
        elif(Model.queries_list[6] == self.query_val):
#             self.courses.join(self.take.groupby('Course ID').mean().Grade)[['Name', 'NAZ', 'Grade']]
              self.df =  self.model.lecturers[self.model.lecturers.Seniority == max(self.model.lecturers.Seniority)]
                
        elif(Model.queries_list[7] == self.query_val):
#             print(self.model.take.join(self.model.courses['Weekly Hours'],'Course ID').groupby('Student ID').sum())
            self.df = self.model.take.join(self.model.courses['Weekly Hours'],'Course ID').groupby('Student ID').sum().join(self.model.students[['First Name','Last Name']],'Student ID')[['First Name','Last Name','Weekly Hours']]
            
        elif(Model.queries_list[8] == self.query_val):
            self.df = self.model.take.join(self.model.courses['NAZ'],'Course ID').groupby('Student ID').sum().join(self.model.students[['First Name','Last Name']],
                                                                                                 'Student ID')[[ 'First Name', 'Last Name', 'NAZ']][self.model.take.join(self.model.courses['NAZ'],'Course ID').groupby('Student ID').sum().join(self.model.students[['First Name','Last Name']],
                                                                                                 'Student ID')[[ 'First Name', 'Last Name', 'NAZ']]['NAZ'] > self.input]
        elif(Model.queries_list[9] == self.query_val):
            self.df = pd.DataFrame(self.model.take.join(self.model.students['School'],on='Student ID').groupby('School').mean().Grade)
            

class View:
    def __init__(self,controller):
        super().__init__()
        self.root = Tk()
        self.controller = controller
        self.title_name = tkinter.Label(self.root,text="MENU".upper())
        self.title_name.pack()
        View.menu_page(self)  
    
    def _make_main_frame(self):
        self.main_frm = ttk.Frame(self.root)
        self.main_frm.pack(padx=10,pady=10,fill=BOTH,expand=True)
    
    def _make_entry(self):
        ent = ttk.Entry(self.main_frm,justify='right')
        ent.pack()
        return ent
    
    def _make_label(self,text):
        label = tkinter.Label(self.main_frm,text=text,font=('Helvetica', 10, 'bold'))
        label.pack(pady=15)
        return label
    
    def menu_page(self):
        self.clear()
        self.root.geometry("800x600")
        frame_btn = tkinter.Frame(self.root)
        frame_btn.pack(anchor="c")
        frame_btn.place(anchor="c", relx=.5, rely=.5)
        self.title('MENU')
 
        self.bn_search = tkinter.Button(master=frame_btn,text="Show",command= self.search_page, height = 5, width = 10,font=('Helvetica', 10, 'bold')).pack(pady=10)
        self.bn_add = tkinter.Button(master=frame_btn,text="Add",command= self.add_page, height = 5, width = 10,font=('Helvetica', 10, 'bold')).pack(pady=10)
        self.bn_remove = tkinter.Button(master=frame_btn,text="Remove",command= self.remove_page, height = 5, width = 10,font=('Helvetica', 10, 'bold')).pack(pady=10)
        self.bn_cancel = tkinter.Button(master=frame_btn,text="Exit",command=self.root.destroy, height = 5, width = 10,font=('Helvetica', 10, 'bold')).pack(pady=10)
        self.main()
        
    def add_page(self):
        self.root.geometry("1000x1000")
        self.clear()
        self.title('ADD')
        self._make_main_frame()
        value_inside = tkinter.StringVar(self.main_frm)
        value_inside.set("Select an Option")
        question_menu = tkinter.OptionMenu(self.main_frm, value_inside, *self.controller.model.search_list,command=self.add_info)
        question_menu.pack()
        frame = Frame(master=self.root).pack()
        Button(master=frame,text="Back",command=self.menu_page).pack(pady=10)
        Button(master=frame,text="Exit",command=self.root.destroy).pack(pady=10)
    
    def remove_page(self):
        self.root.geometry("1000x1000")
        self.clear()
        self.title('REMOVE')
        self._make_main_frame()
        value_inside = tkinter.StringVar(self.main_frm)
        value_inside.set("Select an Option")
        a = ['Students','Lecturers','Courses']
        question_menu = tkinter.OptionMenu(self.main_frm, value_inside, *a)
        question_menu.pack()
        Label(master=self.main_frm,text='Enter ID').pack()
        e = Entry(self.main_frm)
        e.pack()
        Button(master=self.main_frm,text="Remove",command=lambda: self.remove_func(value_inside,e.get())).pack()
        self.l_out = Label(self.main_frm,text='')
        self.l_out.pack()
        frame = Frame(master=self.root).pack()
        self.back = Button(master=frame,text="Back",command=self.menu_page).pack(pady=10)
        self.bn_cancel = Button(master=frame,text="Exit",command=self.root.destroy).pack(pady=10)

    def remove_func(self,value_inside,val):
        if val.isnumeric():
                val = int(val)
                if (value_inside).get().lower() == 'students':
                    if val in self.controller.model.students.index:
                        data = self.controller.model.students.loc[val].values
                        self.l_out.config(text=f'{value_inside.get()} removed! \n {data}',font=('Helvetica', 10, 'bold'))
                        self.controller.model.students.drop(val,inplace=True)
                        self.controller.model.take = self.controller.model.take[self.controller.model.take['Student ID'] != val]
                        self.controller.model.students.to_csv('Students.csv')
                        self.controller.model.take.to_csv('Take.csv') 
                    else:
                        self.l_out.config(text=f'This {value_inside.get()} not exist in the data',font=('Helvetica', 10, 'bold'))
                elif (value_inside).get().lower() == 'lecturers':
                    if val in self.controller.model.lecturers.index:
                        data = self.controller.model.lecturers.loc[val].values
                        self.l_out.config(text=f'{value_inside.get()} removed! \n {data}',font=('Helvetica', 10, 'bold'))
                        self.controller.model.lecturers.drop(val,inplace=True)
                        self.controller.model.lecturers.to_csv('Lecturers.csv')

                    else:
                        self.l_out.config(text=f'This {value_inside.get()} not exist in the data',font=('Helvetica', 10, 'bold'))
                elif (value_inside).get().lower() == 'courses':
                    if val in self.controller.model.courses.index:
                            data = self.controller.model.courses.loc[val].values
                            self.l_out.config(text=f'{value_inside.get()} removed! \n {data}')
                            self.controller.model.courses.drop(val,inplace=True)
                            self.controller.model.courses.to_csv('Courses.csv')
                            self.controller.model.take = self.controller.model.take[self.controller.model.take['Course ID'] != val]
                    else:
                        self.l_out.config(text=f'This {value_inside.get()} not exist in the data',font=('Helvetica', 10, 'bold'))
                else:
                     self.l_out.config(text='Choose table to remove from',font=('Helvetica', 10, 'bold'))
        else:
            self.l_out.config(text='Invalid Input',font=('Helvetica', 10, 'bold'))

    def add_info(self,value_inside):
        self.clean(1)
        if value_inside == 'Students':
            self.df = self.controller.model.students
            self.build_info('Students.csv',value_inside)
        elif  value_inside == 'Lecturers':
            self.df = self.controller.model.lecturers
            self.build_info('Lecturers.csv',value_inside)
        elif  value_inside == 'Courses':
            self.df = self.controller.model.courses
            self.build_info('Courses.csv',value_inside)
        else:
            self.df = self.controller.model.take
            self.build_info('Take.csv',value_inside)   
    
    def build_info(self,path,value_inside): 
        a = []
        if value_inside != 'Take':
            l = Label(master=self.main_frm , text= f'ID',font=('Helvetica', 10, 'bold')).pack(padx= 2)
            b = Entry(master=self.main_frm , text= f'ID',font=('Helvetica', 10, 'bold'))
            b.pack(pady = (0,20))
            a.append(b)
        else:
            a = []
            a.append(str(self.controller.model.take.index.max()+1))
        for i in self.df.columns:
                l = Label(master=self.main_frm , text= f'{i}',font=('Helvetica', 10, 'bold'))
                l.pack(padx= 2)
                b = Entry(master=self.main_frm , text= f'{i}',font=('Helvetica', 10, 'bold'))
                b.pack(pady = (0,20))
                a.append(b)
        Button(master=self.main_frm,text='save',command=lambda:self.save(a,path,value_inside)).pack()        
        self.l_out = tkinter.Label(master=self.main_frm,text = '')
        self.l_out.pack()    
    
    def save(self,a,path,value_inside):
        can_add = True
        if value_inside!= 'Take':
            b = [x.get() for x in a if x.get()!='']
        else:
            b = []
            b.append(a[0])
            b[1:] = [x.get() for x in a[1:] if x.get()!='']
        
        if len(b[1:]) == len(self.df.columns):
            index = self.df.index.name
            for ind,val in enumerate(dict(zip(self.df.columns,b[1:]))):
                   
                    if self.df[val].dtype !='O':
                        if b[ind+1].isnumeric():
                            b[ind+1] = np.int64(b[ind+1])
                        else:
                            can_add = False
            if can_add:
                if b[0].isnumeric():
                    if int(b[0]) not in self.df.index:
                        self.df.loc[b[0]] = b[1:]
                    else: 
                        can_add = False
                        self.l_out.config(fg='red' ,text='ID existed',font=('Helvetica', 10, 'bold'))
                else:
                    can_add = False
                    self.l_out.config(fg='red' ,text='ID need to be integer!',font=('Helvetica', 10, 'bold'))
                if index != None:
                    self.df.to_csv(path,index=True,index_label='ID')
                else:
                    self.df = self.df.append(dict(zip(self.df.columns,b)),ignore_index=True)
                    self.df.reset_index(drop=True, inplace=True)
                    self.df.to_csv(path,index=False)
                if value_inside == 'Students':
                    self.controller.model.students = self.df
                elif  value_inside == 'Lecturers':
                    self.controller.model.lecturers = self.df
                elif  value_inside == 'Courses':
                    self.controller.model.courses = self.df
                else:
                    self.take= self.df
                if can_add:
                    self.l_out.config(fg='blue' ,text='Saved!',font=('Helvetica', 10, 'bold'))
            else:
                self.l_out.config(fg='red' ,text='Invalid input',font=('Helvetica', 10, 'bold'))
        else:
            self.l_out.config(fg='red' ,text='Please, Fill all the entries',font=('Helvetica', 10, 'bold'))
        
    def title(self,name):  
        self.title_name.config(text=name.upper(),font=("Courier", 44))
    
    def search_page(self):
        self.root.geometry("1000x1000")
        self.clear()
        self.title('SHOW TABLES')
        self._make_main_frame()
        value_search = tkinter.StringVar(self.main_frm)
        value_search.set("Select an Table")
        question_menu = tkinter.OptionMenu(self.main_frm, value_search, *Model.search_list,command= self.build)
        question_menu.pack()

        query_val = tkinter.StringVar(self.main_frm)
        query_val.set("Select an Query")
       
        queries_menu = tkinter.OptionMenu(self.main_frm, query_val, *Model.queries_list,command= self.queries_func)
        queries_menu.pack()
        self.back_frame = Frame(master=self.root).pack()
        self.back = Button(master=self.back_frame,text="Back",command=self.menu_page).pack(pady=10)
        self.bn_cancel = Button(master=self.back_frame,text="Exit",command=self.root.destroy).pack(pady=10)
        self.main()
        
    def build(self,value_search):
        list = self.main_frm.winfo_children()
        self.clean(2)
        self.build_table(value_search) 
    
    def clean(self,n):
        list = self.main_frm.winfo_children()
        if len(list)> n: 
            for l in list[n:]:
                l.destroy()
    
    def queries_func(self,query_val):
        list = self.main_frm.winfo_children()
        self.clean(2)
        self.controller.query_val = query_val
        if(Model.queries_list[1] == query_val):
            self._make_label("Please enter age X greater")
            e1 = self._make_entry()
            button = Button(self.main_frm,text="Enter",command=lambda: self.age(e1.get())).pack()
 
        elif(Model.queries_list[2] == query_val):
            self.controller.build_q()
            self.build_query()
            self.graph_bar(x='Name',y='Failed students')
        elif(Model.queries_list[3] == query_val):
            self.controller.build_q()
            self.build_query()
            self.graph_bar(x='Name',y='Grade')
        elif(Model.queries_list[4] == query_val):   
            self.controller.build_q()
            self.build_query()
            self.graph_bar(x='First Name',y='Grade')     
        elif(Model.queries_list[5] == query_val):   
            self._make_label("Please enter ID to the show info")
            e1 = self._make_entry()
            Button(self.main_frm,text="Enter",command=lambda: self.show_course_by_ID(e1.get())).pack()
             
        elif(Model.queries_list[7] == query_val): 
            self.controller.build_q()
            self.build_query()
            self.graph_bar(x='First Name',y='Weekly Hours')
        elif(Model.queries_list[8] == query_val): 
            self._make_label("Please enter NAZ")
            e1 = self._make_entry()
            button = Button(self.main_frm,text="Enter",command=lambda: self.show_student_by_naz(e1.get())).pack()
            
        elif(Model.queries_list[9] == query_val): 
            self.controller.build_q()
            self.build_query()
            self.graph_bar(x='School',y='Grade')
        else:
            self.controller.build_q()
            self.build_query()
            
    def show_course_by_ID(self,x):
        self.clean(5)
        if x.isnumeric():
            self.controller.input = int(x)
            self.controller.build_q()
            self.build_query()
        else:
            self._make_label('Invalid input').config(fg='red',font=('Helvetica', 10, 'bold'))
    
    def graph_bar(self,x,y):
        figure = sns.barplot(y=self.controller.df.reset_index()[y],x=self.controller.df.reset_index()[x]).figure
        plt.Figure(figsize=(15,20))
        canvas = FigureCanvasTkAgg(figure, master=self.main_frm)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH,expand=True)
    
    def age(self,x):
        self.clean(5)
        if x.isnumeric():
            self.controller.input = int(x)
            self.controller.build_q()
            self.build_query()
        else:
            self._make_label('Invalid input').config(fg='red',font=('Helvetica', 10, 'bold'))
   
    def show_student_by_naz(self,x):
        self.clean(5)
        if x.isnumeric():
            self.controller.input = int(x)
            self.controller.build_q()
            if self.controller.df.empty == False:            
                self.build_query()
                self.graph_bar(x='First Name',y='NAZ')
            else:
                self._make_label('NO STUDENTS FOUND')

        else:
            self._make_label('Invalid input').config(fg='red',font=('Helvetica', 10, 'bold'))

    
    def build_query(self):
        if self.controller.df.empty == False:
            f = Frame(self.main_frm)
            f.pack(fill=BOTH,expand=True)
            self.table = pt = Table(f, dataframe=self.controller.df.reset_index(),editable=False)
            pt.autoResizeColumns()
            pt.show()
        else:
            self._make_label('NO STUDENTS FOUND')
    
    def build_table(self,value_search):
        f = Frame(self.main_frm)
        f.pack(fill=BOTH,expand=True)
        if value_search == 'Students':
            df = self.controller.model.students
        elif  value_search == 'Lecturers':
            df = self.controller.model.lecturers
        elif  value_search == 'Courses':
            df = self.controller.model.courses
        else:
            df = self.controller.model.take
        self.table = pt = Table(f, dataframe=df.reset_index(),editable=False)
        pt.show()
        
    
    def clear(self):
        list = self.root.winfo_children()
        for l in list[1:]:
            l.destroy()

    
    def main(self):
        self.root.mainloop()

Controller()