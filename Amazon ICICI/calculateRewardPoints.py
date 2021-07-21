### Imports ###
import getpass
import re
from pdfrw import PdfReader, uncompress
import pikepdf
import imaplib
import os
import email
import datetime


### CONSTANTS ###
DIRECTORY = '/home/gaurav/Other/CcStatement/'
MONTH = input('Bill Generation Month? ')
SUBJECT_ = '"icici bank credit card statement for the period "'
IMAP_URL = 'imap.gmail.com'


def is_date(string):
    if re.search('[0-9]+/[0-9]+/[0-9]+', string):
        return True
    else:
        return False


def decryptPdf(filepath):
    pdf = pikepdf.open(
        filepath+'.pdf', password=getpass.getpass('Password to decrypt PDF file: '))
    pdf.save(filepath+"Readable.pdf")
    return PdfReader(filepath+"Readable.pdf")


def getOnlyDataBetweenDates(lst):
    initial = None
    final = None
    for cnt in range(len(lst)):
        if is_date(lst[cnt]):
            initial = cnt
            break

    for cnt in range(len(lst)-1, 0, -1):
        if is_date(lst[cnt]):
            final = cnt
            break

    if initial != None:
        return lst[initial:final+4]


def getRelevantData(page):
    listOfRelevantData = []
    for line in page.splitlines():
        if 'Tj' in line:
            dataInsideBracket = line[line.find('(')+1:line.rfind(')')]
            listOfRelevantData.append(dataInsideBracket)

    return getOnlyDataBetweenDates(listOfRelevantData)


def isAmazon(str):
    if 'amazon' in str.lower():
        return True
    return False


def points(lst):
    amountInInt = re.sub('\D', '', lst[3])
    if isAmazon(lst[2]):
        per = 0.02*0.01
    else:
        per = 0.01*0.01
    return (float(amountInInt)*per)


def isCredit(lst):
    if 'cr' in lst[3].lower():
        return True
    return False


def getRewardPoints(lst):
    if isCredit(lst):
        return points(lst)*-1
    else:
        return points(lst)


def toSkip(lst):
    if lst == None or 'Payment Received' in lst[2] or 'petrol' in lst[2].lower() or 'fuel surcharge' in lst[2].lower():
        return True
    return False


def calculateAmazonRewardPoints(llst):
    if llst == None:
        return

    # Headers
    csvList = []
    rewards = 0

    for lst in llst:
        if toSkip(lst):
            continue
        try:
            rewardPts = getRewardPoints(lst)
            rewards += rewardPts
            line = lst[0] + "; " + lst[1] + "; " + \
                lst[2] + "; " + lst[3] + "; " + str(isAmazon(lst[2])) + \
                "; " + str(rewardPts) + "\n"
            csvList.append(line)
        except Exception as e:
            print('Error', e)
    return [rewards, csvList]


def downloadAttachmentForMonth():
    email_user = input('Email: ')
    email_pass = getpass.getpass('Password: ')
    con = imaplib.IMAP4_SSL(IMAP_URL)
    con.login(email_user, email_pass)
    con.select('Inbox')
    type, data = con.search(None, 'SUBJECT ' + SUBJECT_)
    id_list = data[0].split()
    for id in id_list:
        typ, data = con.fetch(id, '(RFC822)')
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
        email_month = datetime.datetime.strptime(
            email_message['Date'], '%a, %d %b %Y %H:%M:%S %Z').strftime("%B")
        if email_month.__eq__(MONTH):
            break

    # downloading attachments
    for part in email_message.walk():
        # this part comes from the snipped I don't understand yet...
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()

        if bool(fileName):
            if not os.path.isfile(DIRECTORY+MONTH+'.pdf'):
                fp = open(DIRECTORY+MONTH+'.pdf', 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                print("### Successfully Calculated Reward Points ###")

        subject = str(email_message).split(
            "Subject: ", 1)[1].split("\nTo:", 1)[0]
        print('Downloaded "{file}" from email titled "{subject}" .'.format(
            file=fileName, subject=subject))


def main():
    downloadAttachmentForMonth()
    FILEPATH = DIRECTORY+MONTH
    root = decryptPdf(FILEPATH)
    rewards = 0
    wFile = open(DIRECTORY+MONTH+'Calc.csv', 'w')
    wFile.writelines(
        'Date; SerNo; Description; Amount Spent; Amazon?; RewardPts \n')
    for pageCnt in range(len(root.pages)):
        page = root.pages[pageCnt].Contents
        uncompress.uncompress([page])
        lst = getRelevantData(page.stream)
        if lst != None:
            llst = [[lst[i], lst[i+1], lst[i+2], lst[i+3]]
                    for i in range(0, len(lst), 4)]
            [reward, finalList] = calculateAmazonRewardPoints(llst)
            rewards += reward
            wFile.writelines(finalList)
    wFile.write("\n")
    wFile.write("Reward Points earned in the month of " +
                MONTH + " is " + str(rewards))
    print("\n")
    print("Reward Points earned in the month of " +
          MONTH + " is " + str(rewards))


if __name__ == "__main__":
    main()
