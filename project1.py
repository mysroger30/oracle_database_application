'''
Project 1

Copyright 2016, Zhaorui CHEN(Teppie), Nicholas LI, Jiaxuan YUE

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import sys
import cx_Oracle # the package used for accessing Oracle in Python
import getpass # the package for getting password from user without displaying it
import time
import re

class Connection:
    def __init__(self):
        # FROM Kriti
        # get username
        user = input("Username [%s]: " % getpass.getuser())
        if not user:
            user=getpass.getuser()
	
        # get password
        pw = getpass.getpass()

	# The URL we are connnecting to
        conString=''+user+'/' + pw +'@gwynne.cs.ualberta.ca:1521/CRS'
        self.connection = cx_Oracle.connect(conString)
    
    def doCommit(self):
        self.connection.commit()

    def disconnect(self):
        self.connection.close()

    def executeStmt(self, stmt):
        '''
        execute the given statement but doesn't return anything
        '''
        curs = self.connection.cursor()
        curs.execute(stmt)
        self.connection.commit()
        curs.close()
    
    def fetchResult(self, query):
        '''
        execute the given query to the database and 
        return the result in a list
        '''
        #DEBUG: print(query)
        curs = self.connection.cursor()
        curs.execute(query)
        rows = curs.fetchall() 
        curs.close()
        #DEBUG: print(rows)
        return rows

    def createInsertion(self, table, *args):
        '''
        Return the sql INSERT statement in string
        '''
        insertion = 'INSERT INTO %s VALUES (' % table
        for i in range(0, len(args)-1):
            if args[i]!=None:
                insertion += args[i]
            else:
                insertion += 'NULL'
            insertion += ', '

        insertion+= args[-1]
        insertion+=')'

        return insertion

    def createDeletion(self, table, keyAttr, value):
        return 'DELETE FROM '+table+' WHERE '+keyAttr+'='+value+';'

    def createQuery(self, columns, tables, conditions):
        '''
        Args:
        columns(str)
        tables(str)
        conditions(str)

        return:
        (str): sql query statement
        '''
        return 'SELECT '+columns+' FROM '+tables+' WHERE '+conditions

    def ifExist(self, table, keyAttr, value):
        '''
        check if the key is already existed in the table

        Args:
        table(str)
        keyAttr(str):the name of the primary key attribute
        value(str): the value of query key attribute
        
        Return: Bool
        '''
        query = self.createQuery(keyAttr, table, keyAttr+'='+value)
        try:
            if not self.fetchResult(query)==[]:
                return True
            else:
                return False
        except cx_Oracle.DatabaseError:
            return False

    def createCursor(self):
        return self.connection.cursor()

class application:
    def __init__(self):
        self.connection =  Connection()

    def selectMenu(self):
        selection = 0
        print('#'*80)
        print('Please select from the following programs: ')
        print('1. New Vehicle Registration')
        print('2. Auto Transaction')
        print('3. Driver Licence Registration')
        print('4. Violation Record')
        print('5. Search Engine')
        print('[Q] Quit')
        while not selection:            
            print('#'*80)
            inputStr = input('Please select the index: ')
            selection = {
                '1': 1,
                '2': 2,
                '3': 3,
                '4': 4,
                '5': 5,
                'Q':'Q',
                'q':'Q'
            }.get(inputStr,0)
            if selection==0:
                print('Your input is not valid, please try again')
        return selection

    def end(self):
        print('See you')
        # close cursor if needed
        self.connection.disconnect()
        sys.exit()

    def main(self):
        selection = 0
        while not selection:
            selection = self.selectMenu()
            if selection==1:
                selection = self.newVehicleRegistration() # return 0 to re-select
            elif selection==2:
                selection = self.autoTransaction()
            elif selection==3:
                selection = self.newDriverRegistration()
            elif selection==4:
                selection = self.violationRecord()
            elif selection==5:
                selection = self.searchEngine()
            elif selection=='Q':
                self.end()
        self.end()
        
    def checkFormat(self, value, inputType, misc):
        '''
        helper function to validate the input
        
        Args:
        value(str): the input string
        inputType(str): the sql type which the input string should be cast into
        misc(list/int): the list of miscellaneous properties, eg. length of the integer

        Return:
        (str) the validated input
        '''
        value = value.strip()
        while value=='': #check if the input is blank
            print('Oops, you are not entering anything...')
            value = input('Please re-input: ').strip()

        if inputType=='char': # validate the input for CHAR
            while True:
                if len(value)>=misc:
                    print('Input is too long. Input should have %d characters' % misc)
                    value = input('Please re-input: ').strip()
                else: 
                    return '\''+value+'\''
        elif inputType=='integer': # validate the input for INTEGER
            while True:
                if not value.isdigit():
                    print('Input is not a numeric type')
                    value = input('Please re-input: ').strip()
                else:
                    return value
        elif inputType=='number': # validate the input for NUMBER
            while True:
                # check if is a float
                # NUMBER(a,b)
                # misc[0]:a, misc[1]:b
                try:
                    val = float(value)
                except ValueError:
                    print('Input is not a numeric type')
                    value = input('Please re-input: ').strip()
                    continue

                # special case for year input
                # if the required decimal length is 0
                # then it should accept the inputs without "."
                if misc[1]==0:
                    while len(value)!=misc[0] or not value.isdigit():
                        print('Input should have length of %s'%misc[0])
                        value = input('Please re-input: ').strip()
                    return value
                    

                if value.isdigit():
                    # explicitly cast it into a float string
                    value = value+'.%s'%('0'*misc[1])

                if value[0]=='-':
                    print('Input should be positive')
                    value = input('Please re-input: ').strip()
                    continue                    

                # check if has the correct length
                if len(value)>misc[0]+1:
                    print('Input is too long. Input should have %d digits(including decimal)' % misc[0])
                    value = input('Please re-input: ').strip()
                    continue

                # check if has the correct decimal length
                if not value[-(misc[1]+1)]=='.':
                    print('Input should have max length of %d, and %d decimal digits' % (misc[0],misc[1]))
                    value = input('Please re-input: ').strip()
                    continue
                return value
        elif inputType=='date': #validate the input for DATE
            while True: # proper format: DD-MM-YYYY
                if not len(value)==10:
                    # if is not in the correct length
                    print('Your input should follow "DD-MM-YYYY"')
                    value = input('Please re-input: ').strip()
                    continue
                if value[2]!='-' or value[5]!='-':
                    # if is not using '-' to connect date, month and years
                    print('Your input should follow "DD-MM-YYYY"')
                    value = input('Please re-input: ').strip()
                    continue
                if not (value[:2].isdigit() and value[3:5].isdigit() and value[6:].isdigit()):
                    # if DD, MM or YYYY is not expressed in integers
                    print('Your input should follow "DD-MM-YYYY"')
                    value = input('Please re-input: ').strip()
                    continue
                if int(value[:2])<1 or int(value[3:5])<1 \
                        or int(value[:2])>31 or int(value[3:5])>12:
                    # if DD or MM is out of range
                    print('Date or month is out of range')
                    value = input('Please re-input: ').strip()
                    continue
                else:
                    # convert 'MM' to characters
                    month = {
                        '01': 'JUN',
                        '02': 'FEB',
                        '03': 'MAR',
                        '04': 'APR',
                        '05': 'MAY',
                        '06': 'JUN',
                        '07': 'JUL',
                        '08': 'AUG',
                        '09': 'SEP',
                        '10': 'OCT',
                        '11': 'NOV',
                        '12': 'DEC',
                        }.get(value[3:5])
                    return ('%s-%s-%s'%(value[:2],month, value[6:])) # may cause bug...

    def checkReference(self, table, keyAttr, value, inputType, misc):
        '''
        helper function to validate input and check if the reference key is valid
        '''
        #if inputType == 'char' or inputType == 'date':
        #    value = "'"+value+"'"
        while not self.connection.ifExist(table, keyAttr, value):
            print('%s is not existed in the database'%value)
            value = input('Please re-input: ').strip()
            value = self.checkFormat(value, inputType, misc)
        return value

    def newVehicleRegistration(self):
        '''
        First program.
        '''
        print('#'*80)
        print('Welcome to the new vehicle registration system')

        # acquire for serial no
        inputVal = input('Please enter the serial number: ')
        serialNo = self.checkFormat(inputVal, 'char', 15) #should accept letters
        # if the serial no is already in the database, ask for re-input
        while self.ifSerialNumExist(serialNo):
            print('Vehicle already exist.')
            inputVal = input('Please enter another serial number: ')
            serialNo = self.checkFormat(inputVal, 'char', 15)

        # acquire for sin of the owner
        inputVal = input('Please enter SIN of the primary owner: ')
        # if the sin is not in the database,
        # let the user choose between re-input and register new people
        sin = self.checkFormat(inputVal, 'char', 15)# should accept letters
        while not self.ifSinExist(sin):
            print('Sin NOT VALID.')
            check = 0
            while check!='1' and check!='2':
                check = input('Re-input sin [1] OR register this person to database [2]? ').strip()
            if check=='1':
                inputVal = input('Please enter SIN of the owner: ')
                sin = self.checkFormat(inputVal, 'char', 15)
            elif check=='2':
                self.newPeopleRegistration(sin)
        firstOwnerSin = sin #store the infomation about the first owner

        inputVal = input('Please enter the maker of the vehicle: ')
        maker = self.checkFormat(inputVal, 'char', 20)

        inputVal = input('Please enter the model of the vehicle: ')
        model = self.checkFormat(inputVal, 'char', 20)

        inputVal = input('Please enter the year of production of the vehicle: ')
        year = self.checkFormat(inputVal, 'number', [4,0])

        inputVal = input('Please enter the color of the vehicle: ')
        color = self.checkFormat(inputVal, 'char', 10)

        inputVal = input('Please enter the type id of the vehicle: ')
        typeId = self.checkReference('vehicle_type','type_id',inputVal, 'integer', 1)
        
        # excute insert statement to the corresponding tables
        insertion = self.connection.createInsertion('vehicle', serialNo, maker,\
                                                    model, year, color, typeId)
        self.connection.executeStmt(insertion)
        insertion = self.connection.createInsertion('owner', sin, serialNo, "'y'")
        self.connection.executeStmt(insertion)

        choice=''
        while not (choice=='y' or choice=='n'):
            choice=input('Do you want to register this vehicle with a secondary owner?[y/n]: ')

        if choice=='y':
            # acquire for sin of the secondary owner
            inputVal = input('Please enter SIN of the secondary owner: ')
            # if the sin is not in the database,
            # let the user choose between re-input and register new people
            sin = self.checkFormat(inputVal, 'char', 15)# should accept letters
            while (not self.ifSinExist(sin)) or sin==firstOwnerSin:
                if sin==firstOwnerSin:
                    print('This people is the first owner of the vehicle')
                    sin = self.checkFormat(input('Please re-input: '), 'char', 15)
                    continue
                    
                print('Sin NOT VALID.')
                check = 0
                while check!='1' and check!='2':
                    check = input('Re-input sin [1] OR register this person to database [2]? ').strip()
                    if check=='1':
                        inputVal = input('Please enter SIN of the owner: ')
                        sin = self.checkFormat(inputVal, 'char', 15)
                    elif check=='2':
                        self.newPeopleRegistration(sin) 

            insertion = self.connection.createInsertion('owner', sin, serialNo, "'n'")
            self.connection.executeStmt(insertion)

        print('Succeed')

        while True:
            choice = input('Re-select the program?[y/n]')
            if choice=='y' or choice=='Y':
                return 0 # select other programs
            elif choice=='n' or choice=='N':
                return 'Q' # quit
            else:
                print('Please choose between [y] and [n]')


    def newPeopleRegistration(self, sin):
        '''
        helper function. Only triggered when specific sin
        is not found in the database
        '''
        inputVal = input('Please enter the name of this person: ')
        name = self.checkFormat(inputVal, 'char', 40)

        inputVal = input('Please enter the height of this person: ')
        height = self.checkFormat(inputVal, 'number', [5,2])

        inputVal = input('Please enter the weight of this person: ')
        weight = self.checkFormat(inputVal, 'number', [5,2])

        inputVal = input('Please enter the eye color of this person: ')
        eyeColor = self.checkFormat(inputVal, 'char', 10)

        inputVal = input('Please enter the hair color of this person: ')
        hairColor = self.checkFormat(inputVal, 'char', 10)
        
        inputVal = input('Please enter the address of this person: ')
        addr = self.checkFormat(inputVal, 'char', 50)

        # acquire for gender
        # if the input is not between 'f' and 'm', ask the user to re-input
        gender = input('Please enter the gender of this person[m/f]: ')
        while not self.isGenderCorrect(gender):
            print('Input not correct. Please use "m" or "f" for male or female')
            gender = input('Please re-input[m/f]: ')
            
        # acquire for birthday
        inputVal = input('Please enter the date of birth[DD-MM-YYYY]:')
        birthday = self.checkFormat(inputVal, 'date', 0) 

        insertion = self.connection.createInsertion('people',\
                                                        sin, name, height, weight,\
                                                        eyeColor, hairColor, addr,\
                                                        "'"+gender+"'", "'"+birthday+"'")
        self.connection.executeStmt(insertion)
        print('New people has been successfully registered')
        return

    def isGenderCorrect(self, gender):
        '''
        check if the gender input is correct
        '''
        return gender=='m' or gender=='f' or gender=='M' or gender=='F'

    def isPrimaryOwnerCorrect(self, pri):
        '''
        check if the input for primary owner is correct
        '''
        return pri=='n' or pri=='y' or pri=='Y' or pri=='N'

    def ifTransactionIdExist(self, tId):
        return self.connection.ifExist('auto_sale','transaction_id',tId)

    def ifTicketNoExist(self, tNo):
        '''
        check if the ticket number input has already
        existed in the database
        '''
        return self.connection.ifExist('ticket','ticket_no', tNo)

    def ifSerialNumExist(self, serialNo):
        return self.connection.ifExist('vehicle','serial_no',serialNo)

    def ifSinExist(self, sin):
        return self.connection.ifExist('people','sin',sin)

    def ifLicenceNoExist(self, LicenceNo):
        return self.connection.ifExist('drive_licence','licence_no', LicenceNo)

    def getCurrentDate(self):
        '''
        get the current date from the system
        '''
        day = time.strftime('%d')
        year = time.strftime('%Y')
        mon = time.strftime('%m')
        month = {
            '01': 'JUN',
            '02': 'FEB',
            '03': 'MAR',
            '04': 'APR',
            '05': 'MAY',
            '06': 'JUN',
            '07': 'JUL',
            '08': 'AUG',
            '09': 'SEP',
            '10': 'OCT',
            '11': 'NOV',
            '12': 'DEC',
        }.get(mon)
        return day+'-'+month+'-'+year
    
    def isPrimaryOwner(self, sin, serialNo):
        '''
        helper function to check if the seller is
        actually the primary owner of the vehicle
        '''
        # eg. sin --> "'9000001'"
        # query --> "SELECT is_primary_owner FROM owner WHERE owner_id='9000001' AND vehicle_id='20034'"
        query = "SELECT is_primary_owner FROM owner WHERE owner_id="+sin+" AND vehicle_id="+serialNo
        check = ''
        try:
            check = self.connection.fetchResult(query)[0]
        except IndexError:
            return 2
        if check[0]=='y' or check[0]=='Y':
            return 0
        elif check[0]=='n' or check[0]=='N':
            return 1

    def generateTransactionId(self):
        '''
        Generate and return the transaction id by querying in the database.
        '''
        query = 'SELECT transaction_id FROM auto_sale WHERE transaction_id>=ALL(SELECT transaction_id FROM auto_sale)'
        resultSet = self.connection.fetchResult(query)
        if resultSet==[]:
            return '1'
        else:
            return str(resultSet[0][0]+1)

    def autoTransaction(self):
        print('#'*80)
        print('Welcome to auto transaction system')

        # if the seller is not the primary owner of the vehicle, he cannot sell this vehicle
        # keep acquiring the sin of the seller and serial no of the vehicle
        while True:
            inputVal = input('Please enter SIN of the seller: ')
            sId = self.checkReference('people', 'sin', "'"+inputVal+"'", 'char', 15)
            #print(sId)-->'9000001'

            inputVal = input('Please enter the serial number: ')
            vId = self.checkReference('vehicle', 'serial_no', "'"+inputVal+"'", 'char', 15)
            #print(vId)-->'20034'
            #vId --> "'20034'"

            # check if the vehicle is primarily owned by the people
            # a vehicle could ONLY be sold by its primary owner
            check = self.isPrimaryOwner(sId, vId)
        
            if check==0:
                break
            elif check==1:
                print('The people is not the primary owner, please try another one')
                continue
            elif check==2:
                print('The people doesn\'t own the vehicle at all. Please try another one')
                continue

        # get the buyer id
        # if the buyer doesn't exist in the database, prompt the choices
        inputVal = input('Please enter SIN of the buyer: ')
        bId = self.checkFormat(inputVal, 'char', 15)
        while not self.ifSinExist(bId):
            print('Sin NOT VALID.')
            check = 0
            while check!='1' and check!='2':
                check = input('Re-input buyer\'s sin [1] OR register this person to database [2]? ').strip()
            if check=='1':
                inputVal = input('Please enter SIN of the buyer: ')
                bId = self.checkFormat(inputVal, 'char', 15)
            else:
                self.newPeopleRegistration(bId) 

        #generate the transaction id
        tId = self.generateTransactionId()
        print('transaction id is: %s'%tId)

        #get the date
        sDate = self.getCurrentDate()
        print('Transaction time is: %s'%sDate)

        inputVal = input('Please enter the price of the transction: ')
        price = self.checkFormat(inputVal, 'number', [9,2])
        
        insertion = self.connection.createInsertion('auto_sale', tId, \
                                                    sId, bId, vId, \
                                                    "'"+sDate+"'", price)
        self.connection.executeStmt(insertion)

        # delete all previous owners of this vehicle
        deletion = 'DELETE FROM owner WHERE vehicle_id=%s'%vId
        self.connection.executeStmt(deletion)

        ## set the buyer to the only primary owner for now
        insertion = self.connection.createInsertion('owner', bId, vId, "'y'")
        self.connection.executeStmt(insertion)

        print('Succeed')

        while True:
            choice = input('Re-select the program?[y/n]')
            if choice=='y' or choice=='Y':
                return 0 # select other programs
            elif choice=='n' or choice=='N':
                return 'Q' # quit
            else:
                print('Please choose between [y] and [n]')


    def generateTicketNo(self):
        '''
        Generate and return the ticket number by querying in the database.
        '''
        query = 'SELECT ticket_no FROM ticket WHERE ticket_no>=ALL(SELECT ticket_no FROM ticket)'
        resultSet = self.connection.fetchResult(query)
        print(resultSet)
        if resultSet==[]:
            return '1'
        else:
            return str(resultSet[0][0]+1)

    def violationRecord(self):
        print('#'*80)
        print('Welcome to violation record system.')

        #generate the ticket no
        tNo = self.generateTicketNo()
        print('ticket number is: %s'%tNo)

        inputVal = input('Please enter SIN of the officer: ')
        officerId = self.checkReference('people', 'sin', "'"+inputVal+"'", 'char', 15)
        
        violatorCheck = ''
        violatorCheck = input('Do you identify the violator and his sin?[y]/[n]')
        while not (violatorCheck=='y' or violatorCheck=='Y' or violatorCheck=='n' or violatorCheck=='N'):
            violatorCheck = input('Please select from [y] or [n]')

        inputVal = input('Please enter the serial number of the vehicle: ')
        vId = self.checkReference('vehicle', 'serial_no', "'"+inputVal+"'", 'char', 15)

        if violatorCheck=='y' or violatorCheck=='Y':
            # if violator id is known
            inputVal = input('Please enter SIN of the violator: ')
            violatorId = self.checkReference('people', 'sin', "'"+inputVal+"'", 'char', 15)
        elif violatorCheck=='n' or violatorCheck=='N':
            # if violator id is unknown, select its primary owner
            query = "SELECT owner_id FROM owner WHERE vehicle_id="+vId+" AND is_primary_owner='y'"
            violatorId = self.connection.fetchResult(query)[0][0] #not tested yet
        
        inputVal = input('Please enter the violation type: ')
        vType = self.checkReference('ticket_type', 'vtype', "'"+inputVal+"'", 'char', 10)

        #get the date
        vDate = "'"+self.getCurrentDate()+"'"
        print('Violation date is at %s'%vDate)

        inputVal = input('Please enter the place: ')
        place = self.checkFormat(inputVal, 'char', 20)
        
        inputVal = input('Please enter the description: ')
        descr = self.checkFormat(inputVal, 'char', 1024)

        insertion = self.connection.createInsertion('ticket', tNo,\
                                                        violatorId, vId, officerId,\
                                                        vType, vDate, place, descr)
        self.connection.executeStmt(insertion)

        print('Succeed')

        while True:
            choice = input('Re-select the program?[y/n]')
            if choice=='y' or choice=='Y':
                return 0 # select other programs
            elif choice=='n' or choice=='N':
                return 'Q' # quit
            else:
                print('Please choose between [y] and [n]: ')


    def hasLicence(self,sin):
        '''
        check if a people with the given sin has a drive licence
        '''
        query = 'SELECT licence_no from drive_licence WHERE sin='+sin
        if self.connection.fetchResult(query)==[]:
            return False
        else:
            return True
   
    def ifLicenceNoExist(self, LicenceNo):
        '''
        check if a licence number has already existed
        '''
        return self.connection.ifExist('drive_licence','licence_no', LicenceNo)

    def ifCidExist(self,cId):
        '''
        check if a driving condition id has already existed
        '''
        return self.connection.ifExist('driving_condition','c_id',cId)

    def newDriverRegistration(self):
        '''
        The third program.
        It will allow users to register a people
        with a drive licence, provided that the
        people doesn't has the licence before.
        '''

        print('#'*80)
        print('Welcome the driver licence registration system.')

        # acquire for sin of the new driver
        inputVal = input('Please enter SIN of the new driver: ')
        # if the sin is not in the database,
        # let the user choose between re-input and register new people
        sin = self.checkFormat(inputVal, 'char', 15)# should accept letters
        while not self.ifSinExist(sin):
            print('Sin NOT VALID.')
            check = 0
            while check!='1' and check!='2':
                check = input('Re-input sin [1] OR register this person to database [2]? ').strip()
            if check=='1':
                inputVal = input('Please enter SIN of the new driver: ')
                sin = self.checkFormat(inputVal, 'char', 15)
            elif check=='2':
                self.newPeopleRegistration(sin) 
            else:
                print('Please choose between:')

        if self.hasLicence(sin):
            print('This person already has a driver\'s licence')
            while True:
                choice = input('Re-select the program?[y/n]')
                if choice=='y' or choice=='Y':
                    return 0 # select other programs
                elif choice=='n' or choice=='N':
                    return 'Q' # quit
                else:
                    print('Please choose between [y] and [n]: ')
        
        licence_no = self.checkFormat(input('Please enter the licence number: '),'char',15)
        while self.ifLicenceNoExist(licence_no):
            print('Licence number already exist')
            licence_no = self.checkFormat(input('Please re-input: '),'char',15)

        inputVal = input('Please enter class of the licence: ')
        licence_class = self.checkFormat(inputVal, 'char', 10)

        issuing_date = self.getCurrentDate()
        print('The issuing date is: %s'%issuing_date)
                
        inputVal = input('Please enter expiring date: ')
        expiring_date = self.checkFormat(inputVal, 'date', 1)

        cursor = self.connection.createCursor()
        photo = ''
        while True:
            fileName = input('Please enter the name of the photo file: ')
            try:
                image  = open(fileName,'rb')
            except IOError:
                print('No such file existed')
                fileName = input('Please re-enter the name: ')
                continue
            photo  = image.read()
            break
        
        insert = """insert into drive_licence (licence_no,sin,class,photo,issuing_date,expiring_date) values (:licence_no,:sin,:class,:photo,:issuing_date,:expiring_date)"""
        cursor.execute(insert, {'licence_no':licence_no[1:-1],'sin':sin[1:-1],'class':licence_class[1:-1],'photo':photo,'issuing_date':issuing_date,'expiring_date':expiring_date})
        self.connection.doCommit()
        image.close()
        cursor.close()

        inputChoice = input('Do you want to enter driving condition?[y]/[n]')
        while not (inputChoice=='n' or inputChoice=='N' or inputChoice=='Y' or inputChoice=='y'):
            inputChoice = input('Please select from [y] and [n]: ')

        if inputChoice=='y' or inputChoice=='Y':
            selectedCid=[] # a temp container which stores the driving condition ids previous selected
            finished='n' #check for if the user has finished adding driving conditions
            
            while finished=='n' or finished=='N':
            #create a new entry in restriction for this new licence
                c_id=''
                inputVal = input('Please enter the id of the driving condition: ')
                c_id = self.checkFormat(inputVal,'integer',1)
                
                # if has already select this cid for the licence before
                while c_id in selectedCid: 
                    print('You have already selected this id before')
                    inputVal = input('Please re-enter the id: ')
                    c_id = self.checkFormat(inputVal,'integer',1)
                selectedCid.append(c_id)
                print(selectedCid)

                # if the c_id is in the database
                if self.ifCidExist(c_id):
                    insertion = self.connection.createInsertion('restriction',licence_no, c_id)
                    self.connection.executeStmt(insertion)
                # if the c_id is not in the database, register it in.
                else:
                    print('driving condition id not found.')
                    print('Creating a new driving condition...')
                    inputVal = input('Please enter the driving condition description: ')
                    driveCondition = self.checkFormat(inputVal, 'char', 1024)

                    # insert into driving_condition
                    insertion = self.connection.createInsertion('driving_condition',c_id, driveCondition)
                    self.connection.executeStmt(insertion)

                    # insert into restriction
                    insertion = self.connection.createInsertion('restriction',licence_no, c_id)
                    self.connection.executeStmt(insertion)
       
                print('Successfully add a driving condition')
                finished = input('Have you finished adding driving condition? [y]/[n]')
                while not (finished=='n' or finished=='N' or finished=='Y' or finished=='y'):
                    # ask for if the user need to input another driving condition for the licence
                    finished = input('Please select from [y]/[n]: ')

        print('Succeed')

        while True:
            choice = input('Re-select the program?[y/n]')
            if choice=='y' or choice=='Y':
                return 0 # select other programs
            elif choice=='n' or choice=='N':
                return 'Q' # quit
            else:
                print('Please choose between [y] and [n]: ')


    def searchEngine(self):
        '''
        The fifth program.
        It allows users the search in the database
        for a specific infomation.
        '''
        
        select = 0
        print('#'*80)
        print('Welcome to violation record system.\nPlease select what you want to search for:')
        while not select:
            print('[1]. Search for personal information')
            print('[2]. Search for violation record')
            print('[3]. Search for vehicle history')
            print('[Q]. Back to main menu')
            print('#'*80)
            inputStr = input('Please select the index: ')
            select = {'1': 1 , '2': 2 , '3': 3 , 'Q': 'Q','q':'Q'}.get(inputStr,0)
            if not select:
                select = 0
                print('Your input is invalid, please try again:')
                print('#'*80)
        print('#'*80)

        if select=='Q':
            return 0

        if select==1:
            inputChoice = ''
            inputChoice = input('Search by name? [n] or Search by licence number? [l]')
            while not (inputChoice=='n' or inputChoice=='N' or inputChoice=='l' or inputChoice=='L'):
                inputChoice = input('Please select from [n] and [l]')
          
            while True:
                if inputChoice=='n' or inputChoice=='N':
                    key = input('Please enter the name:')
                    # query for the person with the given name who hold a licence, also with at least one driving condition
                    queryName="select p.sin,name, l.licence_no,addr,birthday,class,description,expiring_date from people p, drive_licence l LEFT JOIN restriction r ON l.licence_no=r.licence_no LEFT JOIN driving_condition d ON r.r_id=d.c_id where p.sin=l.sin AND lower(p.name) like '%"+key.lower()+"%'"
                    resultSet=self.connection.fetchResult(queryName)
                    
                    # query for all people with the given name who hold a licence, w/o driving condition
                    queryNameInPeopleWithLicence="select p.sin,name,addr,birthday from people p, drive_licence l where p.sin=l.sin AND lower(p.name) like '%"+key.lower()+"%'"
                    resultSetPeopleWithLicence=self.connection.fetchResult(queryNameInPeopleWithLicence)
                    
                    # query in the database to see if the person actually exists or not
                    # query for all people with the given name, w/o licence
                    queryNameInPeople="select sin,name,addr,birthday from people where lower(name) like '%"+key.lower()+"%'"
                    resultSetPeople = self.connection.fetchResult(queryNameInPeople)

                    if resultSet==[]: # if didn't find the name who meets the query condition
                        if resultSetPeople==[]: 
                            # if didn't find the name in the database
                            print('The people doesn\'t exist')
                        else:
                            # if has find the name in the database, but the people doesn't have a licence
                            print('He/She doesn\'t have a licence')
                        break
                    
                    print('Query result')
                    for result in resultSet:
                        print(result)
                        print('-'*60)
                        print('name: %s'%result[1])
                        print('licence number: %s'%result[2])
                        print('address: %s'%result[3])
                        print('birthday: %s'%result[4])
                        print('driving class: %s'%result[5])

                        # In order to list all driving conditions
                        query = "SELECT description FROM driving_condition d, drive_licence l, restriction r WHERE d.c_id=r.r_id AND l.licence_no=r.licence_no AND l.licence_no='"+result[2]+"'"
                        # fetch all driving conditions this people has
                        resultS = self.connection.fetchResult(query)
                        #using list comprehesion to print out
                        print('driving condition: %s'%str([dc[0] for dc in resultS]))
                        print('expiring date: %s'%result[7])

                    # if there are people with the same name,
                    # but don't hold a licence
                    # Our program will only list the available info
                    if len(resultSetPeopleWithLicence)!=len(resultSetPeople):
                        print('-'*60)
                        print('There are %d more people with the same name but don\'t hold a licence'%(len(resultSetPeople)-len(resultSetPeopleWithLicence)))
                        
                        # get the set of all people who have the same name but don't hold the licence yet  
                        diffSet = [e for e in resultSetPeople if e not in resultSetPeopleWithLicence]
                        for result in diffSet:
                            print('-'*60)
                            print('name: %s'%result[1])
                            print('address: %s'%result[2])
                            print('birthday: %s'%result[3])
                    break

                elif inputChoice=='l' or inputChoice=='L':
                    key = input('Please enter the licence number:')
                    queryLicence ="select name, l.licence_no,addr,birthday,class,description,expiring_date from people p, drive_licence l, restriction r, driving_condition d where p.sin=l.sin AND l.licence_no=r.licence_no AND r.r_id=d.c_id AND lower(l.licence_no)='"+key.lower()+"'"
                    resultSet=self.connection.fetchResult(queryLicence)
                    if resultSet==[]:
                        print('The licence does not exist')
                        break

                    print('Query result')
                    for result in resultSet:
                        print('-'*60)
                        print('name: %s'%result[0])
                        print('licence number: %s'%result[1])
                        print('address: %s'%result[2])
                        print('birthday: %s'%result[3])
                        print('driving class: %s'%result[4])

                        # In order to list all driving conditions
                        query = "SELECT description FROM driving_condition d, drive_licence l, restriction r WHERE d.c_id=r.r_id AND l.licence_no=r.licence_no AND l.licence_no='"+result[2]+"'"
                        # fetch all driving conditions this people has
                        resultS = self.connection.fetchResult(query)
                        #using list comprehesion to print out
                        print('driving condition: %s'%str([dc[0] for dc in resultS]))
                        print('expiring date: %s'%result[6])
                    break
                
                else:
                    print('The name/id you entered is invalid, please try again')
           
                    print('#'*80)

        elif select==2: # if the user choose the search for violation records
            while True:
                # ask for the input type. User can choose from inputing sin or inputing licence number
                selectInput = input('Would you like to use SIN [1] or licence number [2] to check:')
                if selectInput == '1':
                    inputVal = input('Please input a SIN:')
                    sin = self.checkFormat(inputVal, 'char', 15)
                    while not self.ifSinExist(sin):
                        inputVal = input('SIN not valid, please try again:')
                        sin = self.checkFormat(inputVal,'char',15)
                            
                    # query in the database for all violation records with this sin
                    querySin ="select * from ticket where lower(violator_no)="+sin.lower()
                    resultSet = self.connection.fetchResult(querySin)
                    if resultSet==[]:
                        print('The people does not have violation record yet.')
                        break
                    else:
                        # print out the query result one by one
                        print('Query result')
                        for result in resultSet:
                            print('-'*60)
                            print('ticket number: %s'%result[0])
                            print('violator number: %s'%result[1])
                            print('vehicle id: %s'%result[2])
                            print('officer number: %s'%result[3])
                            print('ticket type: %s'%result[4])
                            queryFine = "select fine from ticket_type where vtype='"+result[4]+"'"
                            fine = self.connection.fetchResult(queryFine)[0][0]
                            print('fine: %s'%str(fine))
                            print('date: %s'%result[5])
                            print('place: %s'%result[6])
                            print('description: %s'%result[7])
                        break

                elif selectInput == '2':
                    inputVal = input('Please input a licence number:')
                    licenceNo = self.checkFormat(inputVal, 'char', 15)
                    while not self.ifLicenceNoExist(licenceNo):
                        inputVal = input('Licence number is not valid, please try again:')
                        licenceNo = self.checkFormat(inputVal,'char',15)
                        
                    # query in the database for the sin corresponding to this licenceNo
                    queryLicence = "select sin from drive_licence where lower(licence_no)="+licenceNo.lower()
                    result = self.connection.fetchResult(queryLicence) #result should be a singleton

                    # query in the database with the sin acquired before
                    querySin ="select * from ticket where lower(violator_no)='"+result[0][0].lower()+"'"
                    resultSet = self.connection.fetchResult(querySin)
                    if resultSet==[]:
                        print('The people does not have violation record yet.')
                        break
                    else:
                        print('Query result')
                        # print out the query result one by one
                        for result in resultSet:
                            print('-'*60)
                            print('ticket number: %s'%result[0])
                            print('violator number: %s'%result[1])
                            print('vehicle id: %s'%result[2])
                            print('officer number: %s'%result[3])
                            print('ticket type: %s'%result[4])
                            queryFine = "select fine from ticket_type where vtype='"+result[4]+"'"
                            fine = self.connection.fetchResult(queryFine)[0][0]
                            print('fine: %s'%str(fine))
                            print('date: %s'%result[5])
                            print('place: %s'%result[6])
                            print('description: %s'%result[7])
                        break

                    break
                else:
                    print('Input invalid. You should choose by entering [1] or [2]')
                    continue

        elif select==3: # if user chooses to browse the vehicle history
            inputVal = input('Please input a serial number:')
            serialNo = self.checkFormat(inputVal,'char',15)
            while not self.ifSerialNumExist(serialNo):
                inputVal = input('Serial number not valid, please try again:')
                serialNo = self.checkFormat(inputVal,'char',15)
                
            query = "select count(transaction_id),avg(price) from auto_sale where lower(vehicle_id)="+serialNo.lower()
            result = self.connection.fetchResult(query)
            
            print('Query result')
            print('-'*60)
            if result[0][0]=='': #if the vehicle haven't been transacted before
                print('The vehicle does not have transaction record before')
            else:
                print('Number of transactions: %s'%result[0][0])
                print('Average price: %s'%result[0][1])
            
            query = "select count(ticket_no) from ticket where lower(vehicle_id)="+serialNo.lower() 
            result = self.connection.fetchResult(query)
            if result[0][0]=='': #if the vehicle doesn't have violation record before
                print('The vehicle does not have violation record before')
            else:
                print('Number of tickets: %s'%result[0][0]) 
            print('-'*60)

        print('#'*80)
        while True:
            choice = input('Re-select the program?[y/n]')
            if choice=='y' or choice=='Y':
                return 0 # select other programs
            elif choice=='n' or choice=='N':
                return 'Q' # quit
            else:
                print('Please choose between [y] and [n]')
        
if __name__ == '__main__':
    app = application()
    app.main()


### DEMO NOTE:
### 1. We automatically generate the licence issuing date and ticket date from the system
### 2. We automatically generate the new ticket_no and new transaction_id from the initial database.
###    Since they are INTEGER, if there is no record in the database, the new id will start with 1.
### 3. We are glad to make any changes to that.
