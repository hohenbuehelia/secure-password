# dependencies: cryptography and fernet

# This is a small program to catalog and database passwords that can be called in other programs securely
# In order to call a specific password from a new program, you will need to add the functions run() and var_recursive()
# You will also need to add the global variables 'keyvar' and 'keymod'
# The documentation around the function one_access_pw will explain how to call the password once the above steps are met

# Note: There is a small issue with pickle that will omit a line from the database until the program is restarted, this
# has something to do with the way the pickle file is populated, but the full iteration of the request does go through
# and the omitted item can be access via a direct call by name given to it in the add to database section

import pickle
import shelve
from cryptography.fernet import Fernet
import getpass
import base64

basefolder = 'THIS NEEDS TO BE CHANGED'  # change to your base folder (example: C:\\users\\test123\\)


# this runs a recursive function to fill your password with 'a' until it hits the 32 byte url friendly size required
# for the crypto key
# this is required to be pasted into any program calling from the database
def var_recursive(x):
    global keyvar
    global keymod
    if x == 32:
        pass
    else:
        keyvar = keyvar + 'a'
        keymod = keymod - 1
        var_recursive(x + 1)


# this sets the crypto key based on anything that you want, best practice would be to use a 32 character password to
# avoid filling with the recursive function
# this is required to be pasted into any program calling from the database
def run():
    global keyvar
    global keymod
    keyvar = getpass.win_getpass(prompt='Input Encryption Key: ', stream=None)
    x = len(keyvar)
    keymod = 32 - x
    if keymod == 0:
        pass
    else:
        var_recursive(x)


# this function allows you to add new or modify existing passwords to the database
# to modify an existing password, simply use the same name the database references, overwrite is default with pickle
def add_passwords():
    data = []
    newdata = []
    pw_file_r = open(basefolder + 'pickle.txt', 'rb')
    while True:
        try:
            data.append(pickle.load(pw_file_r))
        except EOFError:
            break
    pw_file_r.close()

    pwordN = int(input('Enter the number of devices to name: '))
    for i in range(pwordN):
        raw = input('Enter device name ' + str(i) + ' : ')
        newdata.append(raw)

    for x in newdata:
        global keyvar
        data.append(x)
        pw_file_w = open(basefolder + 'pickle.txt', 'ab')
        pickle.dump(x, pw_file_w)
        pw_file_r.close()
        newpass = getpass.win_getpass(prompt='Enter the password for the device ' + x + ': ', stream=None)
        newpass_to_bytes = bytes(newpass, 'utf-8')
        key = base64.urlsafe_b64encode(bytes(keyvar, 'utf-8'))
        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(newpass_to_bytes)
        db_update = shelve.open(basefolder + 'device_shelf.db')
        try:
            db_update[x] = ciphered_text
        finally:
            db_update.close()

    restart = input('Do you want to restart the program? [Yes/No]: ')
    if restart == 'Yes':
        frun()
    else:
        pass


# this function allows the user to pull all of the passwords and unhash them to plaintext and view them
def access_passwords():
    data2 = []
    data2.clear()
    global keyvar
    pw_file_r = open(basefolder + 'pickle.txt', 'rb')
    while 1:
        try:
            data2.append(pickle.load(pw_file_r))
        except EOFError:
            break
    pw_file_r.close()
    for x1 in data2:
        db_read = shelve.open(basefolder + 'device_shelf.db')
        try:
            device = db_read[x1]
        finally:
            db_read.close()
        key = base64.urlsafe_b64encode(bytes(keyvar, 'utf-8'))
        cipher_suite = Fernet(key)
        ciphered_text = device
        unciphered_text = (cipher_suite.decrypt(ciphered_text))
        plaintxt = bytes(unciphered_text).decode('utf-8')
        print('The device ' + x1 + ' has a password of ' + plaintxt)
    restart = input('Do you want to restart the program? [Yes/No]: ')
    if restart == 'Yes':
        frun()
    else:
        pass


# this function allows the user to pull a single password and view it in plaintext
# In order to call the database from another program, paste the entirety of this function where you would like to call
# it. This requires user input to locate the device name in the database, but that can be altered relatively easily.
# In order to use the plaintext password, remove the last six lines (starting with print()) and instead reference
# 'plaintxt' where the password should be entered
def access_one_pw():
    device_name = input('Which device would you like to see? ')
    db_read = shelve.open(basefolder + 'device_shelf.db')
    try:
        device = db_read[device_name]
    finally:
        db_read.close()
    key = base64.urlsafe_b64encode(bytes(keyvar, 'utf-8'))
    cipher_suite = Fernet(key)
    ciphered_text = device
    unciphered_text = (cipher_suite.decrypt(ciphered_text))
    plaintxt = bytes(unciphered_text).decode("utf-8")
    print('The device ' + device_name + ' has a password of ' + plaintxt)
    restart = input('Do you want to restart the program? [Yes/No]: ')
    if restart == 'Yes':
        frun()
    else:
        pass


def frun():

    run()
    decision = input('Do you want to add a new device or alter a password? [Yes/No]: ')

    if decision == 'No':
        decision2 = input('Do you want to view a single device\'s password? [Yes/No]: ')
        if decision2 == 'Yes':
            access_one_pw()
        else:
            if decision2 == 'No':
                decision3 = input('Do you want to see the full database of device passwords? [Yes/No]: ')
                if decision3 == 'Yes':
                    access_passwords()
                else:
                    print('There are no further options. The program is now restarting.')
                    frun()
    else:
        if decision == 'Yes':
            add_passwords()
        else:
            print('Please type Yes or No. The Program is now restarting.')
            frun()


frun()
