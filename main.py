import re
import sys
import json
import subprocess

from random import randint
from pprint import pprint
from subprocess import call
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Setup ORM withh contacts DB 
engine = create_engine('sqlite:///./contacts.db', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()

class Contact(Base):
    __tablename__ = 'CONTACTS'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)
    # date = Column(String)

    def __repr__(self):
        return f'{self.name}, {self.number},'

    def tovoice(self):
        return f'{self.name}, {self.number},'

# State class to keep track of state
class State(Base):
    __tablename__ = 'STATE' # DB table in sqlite

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

    def __repr__(self):
        return f'{self.id}, {self.state},'

def any(items):
    length = len(items)
    random_index = randint(0,length -1)
    random_item = items[random_index]
    return random_item

def today():
    date = datetime.now().replace(microsecond=0).isoformat().replace('T',' ')
    return date

#
# contact api

state = {}
state['INTENT']='ROOT'
state['PREVIOUS_INTENT']='ROOT'
contacts = {}

def add_contact(phone_number,name): # todo: store in sqlite
    global contacts
    # contacts[name] = {'phone_number':phone_number,'name':name}
    # contact = Contact(name=name, number=phone_number, date=today())
    contact = Contact(name=name, number=phone_number)
    session.add(contact)
    session.commit()

def update_contact():
    contact = get_contact_by_name()

    say("Updating "+ contact.name)

    contact.name = state['NEW_CONTACT_NAME']
    session.commit()

def delete_contact():
    global state
    
    if 'CONTACT_NAME' in state:
        contact = session.query(Contact).filter(Contact.name == state['CONTACT_NAME'])
        contact.delete()
        session.commit()
        say("Contact deleted")

    # https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91
    # contact = sesssion.query(Contact).filter(or_(Contact.name == name_or_number, Contact.number == nam_or_number))
    # contact.delete(synchronize_session=False)

def contact_list():
    global contacts
    contacts = session.query(Contact).all()
    return contacts

def get_contact_by_name():
    if 'CONTACT_NAME' in state:
        contacts = session.query(Contact).filter_by(name = state['CONTACT_NAME']).all()
        if contacts:
            for contact in contacts:
                print(contact.name, contact.number)
                return contact
    return None

def setState():
    save_state = State(state=json.dumps(state))
    print(save_state)
    session.add(save_state)
    session.commit()

def getState():
    restore_state = session.query(State)
    if restore_state:
        print(restore_state)
        return restore_state
    
    return False

def say(text):
    print(text)
    subprocess.Popen(["say", text])

def greet_root():
    greetings = [
        "Hi, you can say anything, i.e. create or read or update.",
        "Hi, Let's get started",
        "Hi",
        "Hello",
        "Welcome",
        "Hola",
        "Howdy"
    ]

    say(any(greetings))

def prompt_for_phone_number():
    number_prompts = [
        "Please provide a phone number for the a new contact",
        "Please provide a phone number",
        "Please provide a number",
        "Provide a number",
        "Whats the phone number?",
        "What number would you like to add"
    ]
    say(any(number_prompts))

def prompt_for_name():
    name_prompts = [
        "Please provide a name for the new contact:",
        "Please provide a name:",
        "Please provide a name for the contact:",
        "Provide a name:",
        "What's the contacts name?",
        "What's the name?",
        "Name?"
    ]
    say(any(name_prompts))

def save_and_exit():
    # store the full state
    # print("State: " + json_state().state)
    set_state()
    say("Bye bye!")
    # "Adios",
    # "Quitting",
    # "Our time has come to and end"
    # "See you next time"
    sys.exit(0)

def create_success():
    global state    
    # save to db.
    # clear state
    phone_number = state['CONTACT_PHONE']
    name = state['CONTACT_NAME']

    if 'CONTACT_PHONE' in state:
        del state['CONTACT_PHONE']
    if 'CONTACT_NAME' in state:
        del state['CONTACT_NAME']

    add_contact(phone_number, name)
    say("Contact "+name+" created with phone number:" + phone_number)

def cancel_and_root():
    global state    

    if 'CONTACT_PHONE' in state:
        del state['CONTACT_PHONE']
    if 'CONTACT_NAME' in state:
        del state['CONTACT_NAME']

    say("No Problem!")

def show_list_of_contacts():
    contacts = contact_list()

    if len(contacts) == 1:
        say("There is one contact")
    else:
        say("There are %d  contacts" % (len(contacts),))

    for contact in contacts:
        say(contact.tovoice())


def main():
    global state
    # list of lists
    states = {}

    #ROOT
    states['ROOT'] = {'GREET':greet_root}
    states['ROOT']['TRANSITIONS'] = []
    states['ROOT']['TRANSITIONS'].append({'REGEXEN':['create','set','add'],'DESTINATION':'CREATE'})
    states['ROOT']['TRANSITIONS'].append({'REGEXEN':['read', 'show', 'get', 'list'],'DESTINATION':'READ'})
    states['ROOT']['TRANSITIONS'].append({'REGEXEN':['update', 'replace'],'DESTINATION':'UPDATE'})
    states['ROOT']['TRANSITIONS'].append({'REGEXEN':['delete','remove'],'DESTINATION':'DELETE'})
    states['ROOT']['TRANSITIONS'].append({'REGEXEN':['quit','exit', 'bye', 'goodbye'],'DESTINATION':'EXIT'})
    
    # EXIT
    states['EXIT'] = {'GREET':save_and_exit}
    states['EXIT']['TRANSITIONS'] = []

    # CREATE
    states['CREATE'] = {'GREET':prompt_for_phone_number,'STORE':'CONTACT_PHONE'}
    states['CREATE']['TRANSITIONS'] = []
    states['CREATE']['TRANSITIONS'].append({'REGEXEN':['^[0-9]+$'],'DESTINATION':'CREATE_ASK_FOR_NAME'})
    states['CREATE']['TRANSITIONS'].append({'REGEXEN':['[a-zA-Z ]+'],'DESTINATION':'CREATE'})
    states['CREATE']['TRANSITIONS'].append({'REGEXEN':['cancel'],'DESTINATION':'CANCEL_AND_ROOT'})

    states['CREATE_ASK_FOR_NAME'] = {'GREET':prompt_for_name,'STORE':'CONTACT_NAME'}
    states['CREATE_ASK_FOR_NAME']['TRANSITIONS'] = []
    states['CREATE_ASK_FOR_NAME']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'CREATE_SAVE_CONTACT'})

    states['CREATE_SAVE_CONTACT'] = {'GREET':create_success,'NOPROMPT':1}
    states['CREATE_SAVE_CONTACT']['TRANSITIONS'] = []
    states['CREATE_SAVE_CONTACT']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'ROOT'})

    # CANCEL
    states['CANCEL_AND_ROOT'] = {'GREET':cancel_and_root,'STORE':'CONTACT_PHONE'}
    states['CANCEL_AND_ROOT']['TRANSITIONS'] = []
    states['CANCEL_AND_ROOT']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'ROOT'})

    # READ
    states['READ'] = {'GREET':show_list_of_contacts}
    states['READ']['TRANSITIONS'] = []
    states['READ']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'ROOT'})
    
    # UPDATE
    states['UPDATE'] = {'GREET':prompt_for_name,'STORE':'CONTACT_NAME'}
    states['UPDATE']['TRANSITIONS'] = []
    states['UPDATE']['TRANSITIONS'].append({'REGEXEN':['[a-zA-Z ]+'],'DESTINATION':'UPDATE_NEW_NAME'})
    states['UPDATE']['TRANSITIONS'].append({'REGEXEN':['cancel'],'DESTINATION':'CANCEL_AND_ROOT'})

    states['UPDATE_NEW_NAME'] = {'GREET':get_contact_by_name,'STORE':'NEW_CONTACT_NAME'}
    states['UPDATE_NEW_NAME']['TRANSITIONS'] = []
    states['UPDATE_NEW_NAME']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'UPDATE_CONTACT'})
    states['UPDATE_NEW_NAME']['TRANSITIONS'].append({'REGEXEN':['cancel'],'DESTINATION':'CANCEL_AND_ROOT'})

    states['UPDATE_CONTACT'] = {'GREET':update_contact,'NOPROMPT':1}
    states['UPDATE_CONTACT']['TRANSITIONS'] = []
    states['UPDATE_CONTACT']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'ROOT'})

    states['UPDATE']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'ROOT'})

    # DELETE
    states['DELETE'] = {'GREET':prompt_for_phone_number,'STORE':'CONTACT_PHONE'}
    states['DELETE']['TRANSITIONS'] = []
    states['DELETE']['TRANSITIONS'].append({'REGEXEN':['^[0-9]+$'],'DESTINATION':'DELETE_ASK_FOR_NAME'})
    states['DELETE']['TRANSITIONS'].append({'REGEXEN':['[a-zA-Z ]+'],'DESTINATION':'DELETE'})
    states['DELETE']['TRANSITIONS'].append({'REGEXEN':['cancel'],'DESTINATION':'CANCEL_AND_ROOT'})

    states['DELETE_ASK_FOR_NAME'] = {'GREET':prompt_for_name,'STORE':'CONTACT_NAME'}
    states['DELETE_ASK_FOR_NAME']['TRANSITIONS'] = []
    states['DELETE_ASK_FOR_NAME']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'DELETE_CONTACT'})

    states['DELETE_CONTACT'] = {'GREET':delete_contact,'NOPROMPT':1}
    states['DELETE_CONTACT']['TRANSITIONS'] = []
    states['DELETE_CONTACT']['TRANSITIONS'].append({'REGEXEN':['.*'],'DESTINATION':'ROOT'})

    # this is the main greeter.
    states[state['INTENT']]['GREET']()

    while True:

        #pprint(state)
        sys.stdout.write(state['INTENT'] + ">")


        # Ask for input, only if the state requires it.
        do_prompt = 1
        if 'NOPROMPT' in states[state['INTENT']]:
            if states[state['INTENT']]['NOPROMPT'] == 1:
                do_prompt = 0
    
        user_input = 'NOINPUT'
        if do_prompt == 1:
            user_input = input() # todo noprompt

        if 'STORE' in states[state['INTENT']]:
           state[states[state['INTENT']]['STORE']] = user_input

        possible_transitions = states[state['INTENT']]['TRANSITIONS']

        for transition in possible_transitions:
            regex_list = transition['REGEXEN']
            found = False
            for regex in regex_list:
                # Search through user input for word
                if re.search(regex, user_input, flags=re.IGNORECASE):

                    state['PREVIOUS_INTENT'] = state['INTENT']
                    state['INTENT'] = transition['DESTINATION']
                    found = True
                    break

            if found == True:
                break

        if state['PREVIOUS_INTENT'] != state['INTENT']:
            #only if there was change
            if 'GREET' in states[state['INTENT']]:
                states[state['INTENT']]['GREET']()
            else:
                say(state['INTENT']+" HAS NO GREET()")


        #if user_input == 'quit' or user_input == 'exit':
        #    break


if __name__ == "__main__":
    main() 