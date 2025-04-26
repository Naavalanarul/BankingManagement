import random
import datetime
import mysql.connector as sql
import string
import re
import getpass
import bcrypt

# Database connection
def createDBConnection():
    try:
        return sql.connect(host="localhost", user="root", password="")
    except sql.Error as err:
        print(f"Error: {err}")
        return None

# CIBIL Score Algorithm
def calculateCIBIL(cursor, CCN):
    cursor.execute("SELECT amount, transactionType, date FROM transactionHistory WHERE CCN = %s", (CCN,))
    transactions = cursor.fetchall()

    score = 750  

    onTimePaymentWeight = 50
    creditUtilizationWeight = 30
    transactionBehaviourWeight = 20

    timelyPayments = sum(1 for trans in transactions if trans[1] == "Credit Payment" and trans[0] > 0)

    score += onTimePaymentWeight * timelyPayments

    cursor.execute("SELECT credit, amount FROM transaction WHERE CCN = %s", (CCN,))
    creditData = cursor.fetchone()

    if creditData:
        creditDue, available_balance = creditData
        creditUtilization = creditDue / (available_balance + creditDue) if available_balance + creditDue != 0 else 1
        score -= creditUtilizationWeight * min(creditUtilization, 1) 

    score += transactionBehaviourWeight * len(transactions) // 10 

    return max(300, min(score, 900))

# Functional Algorithms
def captcha():
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(8))

#Email Checking Algorithm
def isEmail(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

#Credit Card Number Generator
def CCN():
    CCNum = [random.randint(0, 9) for _ in range(15)]

    def luhnAlg(CCNum):
        CCNcopy = CCNum[:]
        CCNcopy.reverse()
        total = 0
        for i, num in enumerate(CCNcopy):
            if i % 2 == 0:
                num *= 2
                if num > 9:
                    num -= 9
            total += num
        return total

    checksum = luhnAlg(CCNum)
    check_digit = (10 - (checksum % 10)) % 10
    CCNum.append(check_digit)
    return ''.join(map(str, CCNum))

# Hashing Pin
def hashPin(pin):
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt())

# Checking Hashed Pin
def checkPin(hashed_pin, pin):
    return bcrypt.checkpw(pin.encode(), hashed_pin)

#Hashing Password
def hashPassword(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

#Checking Hashed Password
def checkPassword(hashed_password, password):
    return bcrypt.checkpw(password.encode(), hashed_password)

# Logging transactions to history
def logTransaction(con,cursor, CCN, amount, transactionType):
    date = datetime.date.today()
    time = datetime.datetime.now().time()

    query = """INSERT INTO transactionHistory 
               (CCN, amount, date, time, transactionType) 
               VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query, (CCN, amount, date, time, transactionType))
    con.commit()

# Database creation
def setupDatabase(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS creditCard")
    cursor.execute("USE creditCard")
   
    userDataQuery = """CREATE TABLE IF NOT EXISTS userData (
                       CCN VARCHAR(16) PRIMARY KEY,
                       cardType VARCHAR(12) NOT NULL,
                       CVD DATE,
                       CCCD DATE,
                       ZIPCode INT NOT NULL,
                       Captcha VARCHAR(8),
                       FirstName VARCHAR(30) NOT NULL,
                       SecondName VARCHAR(30) NOT NULL,
                       Pin BINARY(60) NOT NULL,
                       email VARCHAR(100) NOT NULL)"""
    cursor.execute(userDataQuery)

    transactionQuery = """CREATE TABLE IF NOT EXISTS transaction (
                          CCN VARCHAR(16) PRIMARY KEY,
                          amount INT DEFAULT 0,
                          credit INT DEFAULT 0,
                          cardType VARCHAR(12),
                          dateOfCredit DATE,
                          interestPer FLOAT DEFAULT 0.00)"""
    cursor.execute(transactionQuery)

    feedbackQuery = """CREATE TABLE IF NOT EXISTS feedback (
                       Name VARCHAR(50) NOT NULL,
                       feedback VARCHAR(200),
                       dateCreated DATE)"""
    cursor.execute(feedbackQuery)

    transHisQuery = """CREATE TABLE IF NOT EXISTS transactionHistory (
                       CCN VARCHAR(16),
                       amount INT DEFAULT 0,
                       date DATE,
                       time TIME,
                       transactionType varchar(30))"""
    cursor.execute(transHisQuery)

    helpDeskQuery = """CREATE TABLE IF NOT EXISTS helpDesk (
                       ticketID INT AUTO_INCREMENT PRIMARY KEY,
                       CCN VARCHAR(16),
                       issueDesc VARCHAR(255),
                       status VARCHAR(20) DEFAULT 'Open',
                       dateCreated DATE,
                       FOREIGN KEY (CCN) REFERENCES userData(CCN))"""
    cursor.execute(helpDeskQuery)

    adminUserQuery = """CREATE TABLE IF NOT EXISTS adminUsers (
                        username VARCHAR(30) PRIMARY KEY,
                        password BINARY(60) NOT NULL)"""
    cursor.execute(adminUserQuery)

#Help Desk Ticket Function
def submitHelpDeskTicket(cursor, con, CCN, issueDesc):
    dateCreated = datetime.date.today()

    insertQuery = """INSERT INTO helpDesk (CCN, issueDesc, dateCreated) VALUES (%s, %s, %s)"""
    cursor.execute(insertQuery, (CCN, issueDesc, dateCreated))
    con.commit()

    print("Your ticket has been submitted successfully!")

#Admin View for the Ticket Raised Function
def viewHelpDeskTickets(cursor, isAdmin=False):
    query = "SELECT * FROM helpDesk"

    if not isAdmin:
        query += " WHERE CCN = %s"

    cursor.execute(query)
    tickets = cursor.fetchall()

    if tickets:
        print(f"{'Ticket ID':<10} {'Issue Description':<40} {'Status':<10} {'Date Created':<12}")
        for ticket in tickets:
            print(f"{ticket[0]:<10} {ticket[2]:<40} {ticket[3]:<10} {ticket[4]:<12}")

    else:
        print("No tickets found.")

#Status of Ticket Updation
def updateHelpDeskTicketStatus(cursor, con, ticketID, newStatus):
    updateQuery = "UPDATE helpDesk SET status = %s WHERE ticketID = %s"
    cursor.execute(updateQuery, (newStatus, ticketID))
    con.commit()

    print(f"Ticket {ticketID} status has been updated to {newStatus}.")

#Admin User Insertion
def adminUser(cursor,con):
    username1 = "NaavalanArul"
    password1 = "NaavalanArul"
    hashedPass1 = hashPin(password1)

    username2 = ""
    password2 = ""
    hashedPass2 = hashPin(password2)

    username3 = ""
    password3 = ""
    hashedPass3 = hashPin(password3)

    insertAdminQuery1 = "INSERT IGNORE INTO adminUsers VALUES (%s, %s)"
    cursor.execute(insertAdminQuery1, (username1, hashedPass1))
    con.commit()

    insertAdminQuery2 = "INSERT IGNORE INTO adminUsers VALUES (%s, %s)"
    cursor.execute(insertAdminQuery2, (username2, hashedPass2))
    con.commit()

    insertAdminQuery3 = "INSERT IGNORE INTO adminUsers VALUES (%s, %s)"
    cursor.execute(insertAdminQuery3, (username3, hashedPass3))
    con.commit()


# Main Mechanism
def main():
    con = createDBConnection()
    if con is None:
        print("Failed to connect to the database.")
        return
    cursor = con.cursor()
    setupDatabase(cursor)

    while True:

        print("")
        print("\n------------------------------------ BANKING LOGIN PORTAL-----------------------------------")
        print("")
        print("1. Sign In")
        print("2. Sign Up")
        print("3. Update Account")
        print("4. Deactivate Account")
        print("5. Feedback")
        print("6. Transaction History")
        print("7. Help Desk")
        print("8. Admin (View Tickets)")
        print("9. Exit\n")
        print("")
       
        try:
            inputLog = int(input("Enter The Appropriate Option for Login: "))
            print("")
        except ValueError:
            print("Invalid input. Please enter a valid choice.")
            continue

        if inputLog == 1:  # Sign In

            print("")
            print("--------------------------------------SIGN IN PORTAL--------------------------------------")
            print("")

            inputCCN = input("Enter your Credit Card Number: ")
            inputPin = getpass.getpass("Enter your 4-Digit Secure Pin: ")
            stpCCN = inputCCN.strip()
            
            fetchQuery = "SELECT * FROM userData WHERE CCN = %s"
            cursor.execute(fetchQuery, (stpCCN,))
            data = cursor.fetchone()

            if not data:
                print("Credit Card number not found.")
                continue

            elif not checkPin(data[8], inputPin):
                print("Incorrect PIN. Please try again.")
                
                # Captcha Mechanism for Incorrect PIN
                while True:

                    captcha_code = captcha()
                    print(f"Captcha: {captcha_code}")
                    user_captcha = input("Enter the captcha to proceed: ")

                    if user_captcha == captcha_code:
                        print("Captcha verified. You may now try signing in again.")
                        break
                    else:
                        print("Incorrect captcha. Please try again.")
                continue

            fullName = f"{data[6]} {data[7]}"
            dateExp = data[2].strftime('%m/%y')
            cardType = data[1]

            print(f"------------------------------------------------------")
            print(f"|                    CREDIT CARD                      |")
            print(f"|                                                     |")
            print(f"|                                                     |")
            print(f"| Card Holder's Name: {fullName:<29} |")
            print(f"| Card Number: {inputCCN:<34} |")
            print(f"| Card Type: {cardType:<36} |")
            print(f"| Expiry Date: {dateExp:<37} |")
            print(f"|                                                     |")
            print(f"|                                                     |")
            print(f"|                                                     |")
            print(f"------------------------------------------------------")

            while True:

                print("")
                print("\n---------------------------------BANKING PORTAL------------------------------------")
                print("")
                print("1. Check Balance")
                print("2. Pay Credit")
                print("3. Transfer Money")
                print("4. Deposit")
                print("5. Get Credit")
                print("6. Log out")
                print("")

                try:
                    userOpt = int(input("Enter the Appropriate Choice: "))
                except ValueError:
                    print("Invalid choice. Please select a valid option.")
                    continue

                if userOpt == 1: # Check balance

                    transQuery = "SELECT amount, credit FROM transaction WHERE CCN = %s"
                    cursor.execute(transQuery, (inputCCN,))
                    transData = cursor.fetchone()

                    if transData:
                        print(f"Available Balance: {transData[0]}")
                        print(f"Credit Due: {transData[1]}")
                    else:
                        print("No transactions found.")
                
                elif userOpt == 2: # Pay credit

                    currentCreditQuery = "SELECT * FROM transaction where CCN = %s"
                    cursor.execute(currentCreditQuery, (inputCCN,))
                    data = cursor.fetchone()

                    creditAmt = data[2]
                    print(f"Your Current Credit Is {creditAmt}")

                    if creditAmt == 0:
                        print("You have No Credit Remaining to Pay.")

                    else:
                        try:
                            inputPay = int(input("Enter Amount to Pay Your Credit: "))
                        except ValueError:
                            print("Invalid amount entered.")
                            continue

                        if inputPay > creditAmt:
                            print(f"You Cannot pay more than your current credit Amount ({creditAmt}).")

                        else:
                            updateCreditQuery = "UPDATE transaction SET credit = credit - %s WHERE CCN = %s"
                            cursor.execute(updateCreditQuery, (inputPay, inputCCN))
                            con.commit()

                            print(f"Credit of {inputPay} has been paid.")

                            transactionType = "Credit Payment"
                            logTransaction(con,cursor, inputCCN, inputPay, transactionType)


                elif userOpt == 3: # Transfer money

                    inputCCN2 = input("Enter the recipient's Credit Card Number: ")

                    try:
                        inputPay = int(input("Enter Amount to transfer: "))
                    except ValueError:
                        print("Invalid amount entered.")
                        continue

                    if inputCCN == inputCCN2:
                        print("You cannot transfer money to yourself.")
                        continue

                    cursor.execute("SELECT * FROM userData WHERE CCN = %s", (inputCCN2,))
                    recipient = cursor.fetchone()

                    if recipient:
                        updateAmountQuery = "UPDATE transaction SET amount = amount - %s WHERE CCN = %s"
                        cursor.execute(updateAmountQuery, (inputPay, inputCCN))
                        con.commit()

                        updateAmountQuery = "UPDATE transaction SET amount = amount + %s WHERE CCN = %s"
                        cursor.execute(updateAmountQuery, (inputPay, inputCCN2))
                        con.commit()

                        print(f"Transferred {inputPay} to {inputCCN2}.")

                        transactionType2 = "Deposit"
                        transactionType1 = "Withdrawal"
                        logTransaction(con,cursor, inputCCN, inputPay, transactionType1)
                        logTransaction(con,cursor, inputCCN2, inputPay, transactionType2)

                    else:
                        print("Recipient Account not found.")

                elif userOpt == 4: # Deposit money

                    try:
                        inputDep = int(input("Enter amount to deposit: "))
                    except ValueError:
                        print("Invalid amount entered.")
                        continue

                    updateAmountQuery = "UPDATE transaction SET amount = amount + %s WHERE CCN = %s"
                    cursor.execute(updateAmountQuery, (inputDep, inputCCN))
                    con.commit()

                    print(f"{inputDep} has been deposited to your account.")

                    transactionType = "Deposit" 
                    logTransaction(con,cursor, inputCCN, inputDep, transactionType)
                

                elif userOpt == 5: # Get credit

                     cibil_score = calculateCIBIL(cursor, inputCCN)
                     print(f"Your current CIBIL score is: {cibil_score}")
 
                     if cibil_score < 600:
                         print("Your CIBIL score is too low to be eligible for additional credit.")
                     else:
                         try:
                             creditInput = int(input("Enter credit amount: "))
                         except ValueError:
                             print("Invalid credit amount entered.")
                             continue
 
                         # Credit limit logic
                         currentCreditQuery = "SELECT * FROM transaction where CCN = %s"
                         cursor.execute(currentCreditQuery, (inputCCN,))
                         data = cursor.fetchone()
                         creditAmt = data[2]
 
                         if creditInput + creditAmt > 4999000:
                             print("Your request exceeds the maximum credit limit.")
                         else:
                             updateCreditQuery = "UPDATE transaction SET credit = credit + %s + credit*interestPer, amount = amount + %s WHERE CCN = %s"
                             cursor.execute(updateCreditQuery, (creditInput, creditInput, inputCCN))
                             con.commit()
 
                             print(f"Credit of {creditInput} granted.")

                             transactionType = "Credit"
                             logTransaction(con,cursor, inputCCN, creditInput, transactionType)

                elif userOpt == 6: # Log out
                    print("You have successfully logged out.")
                    break

        elif inputLog == 2:  # Sign Up

            print("")
            print("------------------------------------SIGN UP PAGE------------------------------------")
            print("")

            inputFirst = input("Enter Your Respective First Name: ")
            print("")
            inputSecond = input("Enter Your Respective Second Name: ")
            print("")
            inputEmail = input("Enter Your Valid Email: ")
            print("")

            if not isEmail(inputEmail):
                print("Invalid Email Format Given.")
                continue

            inputZip = int(input("Enter your Respective Zip Code : "))
            print("")
    
            while True:

                inputPin = getpass.getpass("Create a Secure 4-Digit Pin : ")
                inputPinCon = getpass.getpass("Confirm Your 4-Digit Secure Pin : ")

                if inputPin == inputPinCon:
                    break
                else:
                    continue

            hashed_pin = hashPin(inputPin)
            newCCN = CCN()
            captchaCode = captcha()

            print("")
            print(f"Captcha: {captchaCode}")
            print("")

            # Card Type Selection
            cardOptions = ['Discover', 'MasterCard', 'AMEX', 'Visa']

            while True:
                print("Card Options:\n 1. Discover\n 2. MasterCard\n 3. AMEX\n 4. Visa\n")
                cardInput = input("Choose your Card Type by entering the respective number : ")

                if cardInput in ['1', '2', '3', '4']:
                    cardType = cardOptions[int(cardInput) - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            #Card Type Selection End

            #Interest Percentage Determination
            interestPer = 0
            if cardType == 'MasterCard':
                interestPer = 0.2151
            elif cardType == 'Discover':
                interestPer = 0.2354
            elif cardType == 'AMEX':
                interestPer = 0.2456
            elif cardType == 'Visa':
                interestPer = 0.2274
            else: 
                continue
            #End of Interest Percentage
            
            print("")
            captchaInput = input("Enter the Captcha to Verify: ")

            if captchaInput.strip() == captchaCode:
                CVD = datetime.date.today() + datetime.timedelta(days=365*7)
                CCCD = datetime.date.today()

                insertQuery = """INSERT INTO userData (CCN, cardType, CVD, CCCD, ZIPCode, Captcha, FirstName, SecondName, Pin, email)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(insertQuery, (newCCN, cardType, CVD, CCCD, inputZip, captchaCode, inputFirst, inputSecond, hashed_pin, inputEmail.strip()))
                con.commit()

                print(f"Sign Up Successful! Your Card Type is {cardType} and Expiry Date is {CVD}.")

                insertTrans = "INSERT INTO transaction (CCN, cardType, interestPer) VALUES (%s, %s, %s)"
                cursor.execute(insertTrans, (newCCN, cardType, interestPer))
                con.commit()

                print("")
                print(f"New Credit Card Number Generated: {newCCN}")

            else:
                print("Incorrect Captcha. Try Again.")

        elif inputLog == 3:  # Update Account

            print("")
            print("---------------------------------UPDATION PORTAL----------------------------------------")
            print("")

            inputCCN = input("Enter your Credit Card Number : ")
            inputPin = getpass.getpass("Enter Your 4-Digit Secure Pin : ")
            inputPinCon = getpass.getpass("ENTER YOUR 4-Digit Secure Pin Again to Confirm : ")
            stpCCN = inputCCN.strip()

            fetchQuery = "SELECT * FROM userData WHERE CCN = %s"
            cursor.execute(fetchQuery, (stpCCN, ))
            data = cursor.fetchone()

            if inputPin == inputPinCon:
                if not data:
                    print("Account not found.")
    
                elif checkPin(data[8], inputPin):
                    while True:

                        print("")
                        print("1. First Name Updation")
                        print("2. Second Name Updation")
                        print("3. Email Updation")
                        print("4. PIN Updation")
                        print("5. ZIP Code Updation")
                        print("6. Exit Upadtion Portal")
                        print("")
        
                        inputUpd = int(input("Enter the Prior Choice for Updation : "))
    
                        if inputUpd == 1:
                            inputNewFirstName = input("Enter Your New First Name : ")
    
                            updateQuery = "UPDATE userData SET FirstName = %s WHERE CCN = %s"
                            cursor.execute(updateQuery, (inputNewFirstName, inputCCN))
                            con.commit()
    
                            print("First Name Updated Successfully.")
    
                        elif inputUpd == 2:
                            inputNewSecondName = input("Enter Your New Second Name : ")
    
                            updateQuery = "UPDATE userData SET SecondName = %s WHERE CCN = %s"
                            cursor.execute(updateQuery, (inputNewSecondName, inputCCN))
                            con.commit()
    
                            print("Second Name Updated Successfully.")
    
                        elif inputUpd == 3:
                            new_email = input("Enter your new email: ")
    
                            if isEmail(new_email):
                                updateQuery = "UPDATE userData SET email = %s WHERE CCN = %s"
                                cursor.execute(updateQuery, (new_email, inputCCN))
                                con.commit()
    
                                print(f"Email updated successfully.")
    
                            else:
                                print("Invalid email format.")
    
                        elif inputUpd == 4:
                            inputNewPIN = input("Enter Your New PIN : ")
    
                            if len(inputNewPIN) == 4 and inputNewPIN.isdigit():
                                updateQuery = "UPDATE userData SET PIN = %s WHERE CCN = %s"
                                cursor.execute(updateQuery, (inputNewPIN, inputCCN))
                                con.commit()
    
                                print("PIN Updated Successfully.")
    
                            else:
                                print("Invalid PIN. Please enter 4 digit numeric value.")
    
                        elif inputUpd == 5:
                            inputNewZIP = int(input("Enter Your New Zip Code : "))
                            if inputNewZIP >= 10000 and inputNewZIP <= 99999:
                                updateQuery = "UPDATE userData SET ZipCode = %s WHERE CCN = %s"
                                cursor.execute(updateQuery, (inputNewZIP, inputCCN))
                                con.commit()
                                print("Zip Code Updated Successfully.")
                            else:
                                print("Invalid Zip Code. Please enter Proper ZIP Code.")
    
                        elif inputUpd == 6:
                            print("Exiting ...")
                            break

                else:
                   print("Invalid Input Given...")

            else:
                print("Invalid Pin Confirmation. Try Again...")

                
        elif inputLog == 4:  # Deactivate Account
            
            print("")
            print("--------------------------------DEACTIVATION PORTAL-------------------------------------")
            print("")


            inputCCN = input("Enter your Credit Card Number : ")
            inputPin = getpass.getpass("Enter your 4-Digit Secure Pin : ")
            inputPinCon = getpass.getpass("Enter Your 4-Digit Secure Pin Again to Confirm : ")
            stpCCN = inputCCN.strip()

            fetchQuery = "SELECT * FROM userData WHERE CCN = %s"
            cursor.execute(fetchQuery, (stpCCN, ))
            data = cursor.fetchone()

            if inputPin == inputPinCon:

                if not data:
                    print("Account not found.")
    
                elif checkPin(data[8], inputPin):
                    deactivateQuery = "DELETE FROM userData WHERE CCN = %s"
                    cursor.execute(deactivateQuery, (inputCCN,))
                    con.commit()
    
                    deactivateQueryT = "DELETE FROM transaction WHERE CCN = %s"
                    cursor.execute(deactivateQueryT, (inputCCN,))
                    con.commit()
    
                    print(f"Account {inputCCN} has been deactivated successfully.")

                else:
                    print("Incorrect Pin. Please try again.")

            else:
                print("Enter Your 4-Digit Secure Pin Properly. Please try again.")


        elif inputLog == 5:  # Feedback
            
            print("")
            print("---------------------------------FEEDBACK PORTAL----------------------------------------")
            print("")

            inputName = input("Enter your name: ")
            inputFeedback = input("Please share your feedback: ")

            dateCreated = datetime.date.today()

            insertQuery = "INSERT INTO feedback (Name, feedback, dateCreated) VALUES (%s, %s, %s)"
            cursor.execute(insertQuery, (inputName, inputFeedback, dateCreated))
            con.commit()
            print(f"Thank you {inputName} for your feedback!")


        elif inputLog == 6:  # Transaction History

            print("")
            print("----------------------------------TRANSACTION HISTORY-----------------------------------")
            print("")

            inputCCN = input("Enter your Credit Card Number: ")

            historyQuery = "SELECT * FROM transactionHistory WHERE CCN = %s"
            cursor.execute(historyQuery, (inputCCN,))
            history = cursor.fetchall()

            if history:
                print(f"{'Date':<12} {'Time':<10} {'Amount':<10} {'Type':<12}")
                for row in history:
                    print(f"{row[2]}  {row[3]}    {row[1]}      {row[4]}")
            else:
                print("No transaction history available.")


        elif inputLog == 7:  #Help Desk Ticket Submission

            print("")
            print("-----------------------------------------HELP DESK---------------------------------------")
            print("")

            inputCCN = input("Enter your Credit Card Number : ")
            issueDesc = input("Enter a Description of your Issue : ")

            submitHelpDeskTicket(cursor, con, inputCCN, issueDesc)

        elif inputLog == 8: #Admin View Help Desk Tickets

            print("")
            print("---------------------------------------ADMIN LOGIN---------------------------------------")
            print("")

            adminUser(cursor,con)

            username = input("Enter Your Admin Username : ")
            password = getpass.getpass("Enter The Respective Admin Password : ")
            
            cursor.execute("SELECT password FROM adminUsers WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result and checkPin(result[0], password):
                while True:

                    print("")
                    print("1. View All Tickets Raised")
                    print("2. Update Ticket Status")
                    print("3. Logout")
                    print("")

                    adminOpt = input("Enter the Appropriate choice for the Login : ")

                    if adminOpt == "1":
                        viewHelpDeskTickets(cursor, isAdmin=True)

                    elif adminOpt == "2":
                        selectTicQuery = "SELECT * FROM helpDesk"
                        cursor.execute(selectTicQuery)
                        tickets = cursor.fetchall()

                        if tickets : 
                            ticketID = int(input("Enter Ticket ID to update : "))
                            newStatus = input("Enter New status (Open, In Progress, Closed) : ")
    
                            updateHelpDeskTicketStatus(cursor, con, ticketID, newStatus)

                        else:
                            print("No Tickets Raised Till Now...")

                    elif adminOpt == "3":
                        print("Logging out...")
                        break

                    else:
                        print("Invalid Input Given.")

            else:
                print("Invalid Username or Password Entered.")
                return False
        elif inputLog == 9:
            print("Logging out...")
        elif inputLog == 9:  # Exit
            print("Exiting. Thank you!")
            break


if __name__ == "__main__":
    main()
