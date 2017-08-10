from requests_ntlm import HttpNtlmAuth
from pyvirtualdisplay import Display
from selenium import webdriver
from time import sleep
import requests
import facebook
import datetime
import base64
import time


# http://nodotcom.org/python-facebook-tutorial.html
# https://developers.facebook.com/tools/explorer/444970989006618

time_to_check = ['00', '10', '20', '30', '40', '50', '05', '15', '25', '35', '45', '55']
lectures_url = 'http://moodle.mcast.edu.mt/course/view.php?id=327'
current_class = 'CSN-6.3A'
ATS_Asgt_url = 'http://ict.mcast.edu.mt/atsstudent/MyAssignments.aspx'
ATS_url = 'http://ict.mcast.edu.mt/atsstudent'


def check_lectures():
    exec_start_time1 = time.time()
    email_message = ''
    driver = ''
    display = ''
    try:
        write_html('Time: ' + time.strftime("%H:%M") + ' Checking Cancelled Lectures \n')
        if check_website(lectures_url):
            cancelled = ''
            display = Display(visible=0, size=(1920, 1080))
            display.start()
            driver = webdriver.Firefox()
            driver.get(lectures_url)
            driver.find_element_by_id('username').send_keys('MOODLE_USERNAME_HERE')
            driver.find_element_by_id('password').send_keys(base64.b64decode('MOODLE_Password_HERE').decode("utf-8"))
            driver.find_element_by_id('loginbtn').click()
            abs_lec = driver.find_element_by_xpath('//*[@id="section-1"]/div[3]').text
            abs_lec_split = abs_lec.split('\n')
            today = (datetime.datetime.now()).strftime("%A")    # Define which subjects you have in which particular day
            if today == "Monday":
                todays_lec = ['database', 'project', 'networking security']
            elif today == "Tuesday":
                todays_lec = ['project', 'advanced networking']
            elif today == "Wednesday":
                todays_lec = ['project', 'advanced networking']
            elif today == "Thursday":
                todays_lec = ['database', 'advanced networking', 'networking security']
            elif today == "Friday":
                todays_lec = ['project', 'networking security', 'database']
            else:
                todays_lec = ['NO SCHOOL TODAY!']
            for line in abs_lec_split:
                if current_class in line:
                    for lectures in todays_lec:
                        if lectures in line.lower():
                            cancelled = cancelled + line
                        del lectures
                del line
            driver.quit()
            display.stop()
            write_html('Cancelled Lectures info Received \n')
            snd_message = check_notice(abs_lec.encode('utf-8'))
            if snd_message and cancelled != '':
                email_message = 'Below please find Cancelled lectures info:\n\n' + cancelled
                group_post(str(email_message), 'GROUP ID NO', "LEC")
            else:
                write_html('Cancelled Lectures still the same, E-mail not sent!')
            del cancelled
            del abs_lec
            del abs_lec_split
            del snd_message
            del driver
            del display
            del todays_lec
            del today
        else:
            write_html('Website Unreachable!')
    except Exception as err1:
        driver.quit()
        display.stop()
        status1, err_msg1 = update_log(str(err1), 'Error Origin: Cancelled Lectures Script')
        write_html(status1)
        del err1
        del status1
        del err_msg1
        del driver
        del display
    time_took1 = time.time() - exec_start_time1
    write_html('\nScript took ' + ("%.2f" % time_took1) + ' seconds to complete \n')
    del exec_start_time1
    del email_message
    del time_took1


def check_ats():
    exec_start_time2 = time.time()
    try:
        if check_website(ATS_url):
            write_html('Time: ' + time.strftime("%H:%M") + ' Checking ATS Notifications \n')
            session = requests.session()
            session.auth = HttpNtlmAuth('mcast\\MCAST_USERNAME', base64.b64decode('PASSWORD').decode("utf-8"))
            ats_items = session.get(ATS_url)
            for ats_item in ats_items:
                if str(ats_item).startswith("__ctl2_lblNotifierContent"):
                    ats_noti_list = str(ats_item).split('>')
                    ats_noti = ats_noti_list[1].replace('</a', '')
                    if ats_noti != 'No unread notices.':
                        write_html('ATS Notices Information Collected\n')
                        email_message = 'You have unread notices in you ATS account!\n' + '\nATS link: ' + ATS_url
                        group_post(str(email_message), '352251615112950', "ATS")
                        del email_message
                    elif ats_noti == 'No unread notices.':
                        write_html('No Unread notices!!')
                    del ats_item, ats_noti_list, ats_noti
            del session, ats_items
            check_assignments()
        else:
            write_html('Website Unreachable')
    except Exception as err2:
        write_html('\nError Occurred!!')
        status2, err_msg2 = update_log(str(err2), 'Error Origin: ATS Script')
        write_html(status2)
        del status2
        del err2
        del err_msg2
    time_took2 = time.time() - exec_start_time2
    print('\nScript took ' + ("%.2f" % time_took2) + ' seconds to complete\n')
    del exec_start_time2
    del time_took2


def check_assignments():
    write_html('Checking for new Assignments...')
    driver = ''
    display = ''
    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()         # Auto logon via firefox plugin
        profile = webdriver.FirefoxProfile(
            profile_directory=r"/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/SeleniumProfile/16ykebtq.Seleniumprofile")
        profile.add_extension(r"/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/SeleniumProfile/seleniumDriver/autoauth-2.1-fx+fn.xpi")
        driver = webdriver.Firefox(firefox_profile=profile)
        driver.get(ATS_Asgt_url)
        sleep(2)
        driver.find_element_by_xpath('//*[@id="cmbSemester"]/option[2]').click()
        sleep(2)
        current_assignments = []
        file = open(r"/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/ATS_assignments.txt", "a+")
        file.seek(0)
        for ln in file:
            current_assignments.append(ln.strip('\n'))
            del ln
        try:
            table_id = driver.find_element_by_id('dgMaterialVerification')
            rows = table_id.find_elements_by_tag_name('tr')
            for row in rows:
                unt = row.find_elements_by_tag_name("td")[3]
                col = row.find_elements_by_tag_name("td")[5]
                st_ty = row.find_elements_by_tag_name("td")[7]
                unit_name = unt.text
                ass_title = col.text
                ass_sit_type = st_ty.text
                assignment = ass_title + ' ' + ass_sit_type
                if assignment not in current_assignments:
                    file.write(assignment + '\n')
                    write_html('ATS Assignment Information Collected\n')
                    email_message = 'You have New Assignments on ATS!\n\t' + 'Assignment Title: ' + ass_title + ', ' + ass_sit_type + ' (' + unit_name + ')\n\nATS link: ' + ATS_Asgt_url
                    group_post(str(email_message), 'GROUP ID NO ', "ATS_Assignments")
                    del email_message
            del row, col, ass_title, table_id, rows, ass_title
        except:
            pass
        file.close()
        driver.quit()
        display.stop()
    except Exception as err2:
        driver.quit()
        display.stop()
        write_html('\nError Occurred!!')
        status2, err_msg2 = update_log(str(err2), 'Error Origin: ATS Assignment Script')
        write_html(status2)
        del status2
        del err2
        del err_msg2


def check_website(url_to_check):  # noinspection PyBroadException
    check = ''
    try:
        check = requests.get(url_to_check)
        if check.status_code == 200 or check.status_code == 401:
            del check
            del url_to_check
            return True
        else:
            del check
            del url_to_check
            return False
    except:
        del check
        del url_to_check
        return False


def check_notice(abs_notice):
    info = ''
    file = open(r'/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/previous_saved_notices.txt', "a+")
    file.seek(0)
    for line in file:
        info += line
        del line
    if info == abs_notice:
        snd_email = False
    else:
        file.seek(0)
        file.truncate()
        file.seek(0)
        file.write(abs_notice)
        snd_email = True
    file.close()
    del abs_notice
    del info
    del file
    return snd_email


def update_log(log, err_origin):
    file = open(r'/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/errors_log_file.txt', "a")
    e_msg = datetime.datetime.now().strftime("%d-%m-%Y %H:%M") + '\n' + err_origin + '\n' + log
    msg = datetime.datetime.now().strftime("%d-%m-%Y %H:%M") + '\n' + err_origin + '\n' + log + '\n\n'
    file.write(msg)
    file.close()
    rtn_saved = 'Error Occurred and Log file Updated!!'
    email_message = 'Error Occurred: ' + e_msg
    del log
    del err_origin
    del file
    del msg
    del e_msg
    return rtn_saved, email_message


def write_html(html_msg):
    print(html_msg)
    html_path = r"/var/www/html/Tasks/tasks.html"
    file = open(html_path, "a")
    file.write('<p>' + html_msg + '</p>' + '\n')
    file.close()
    del html_msg
    del html_path
    del file


def group_post(msg, group_id, opt):
    try:
        post = False
        if group_id == 'GROUP ID NO':  # Group ID of School FB Group.
            if opt == "LEC":
                file_to_open = r'/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/LEC_last_post.txt'
            elif opt == "ATS":
                file_to_open = r'/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/ATS_last_post.txt'
            elif opt == "ATS_Assignments":
                file_to_open = r'/home/Python_User/LogFiles/ATSNoticesAndCancelledLectures/RequiredFiles/ATS_ass_last_post.txt'
            else:
                file_to_open = ''
            file = open(file_to_open, "a+")
            file.seek(0)
            info = ''
            for line in file:
                info += line
                del line
            if info == datetime.datetime.now().strftime("%d-%m-%Y"):
                write_html('Already Posted on FB today. No Spammin!')
            else:
                post = True
                file.seek(0)
                file.truncate()
                file.seek(0)  # sets the pointer to line 0
                file.write(datetime.datetime.now().strftime("%d-%m-%Y"))
            file.close()
            del file
            del info
            del file_to_open
        if post or group_id != 'GROUP ID NO':
            oauth_access_token = 'ACCESS TOKEN FROM FB'
            graph = facebook.GraphAPI(oauth_access_token)
            graph.put_object(group_id, "feed", message=msg)
            write_html('FB Group Message Posted!')
            del oauth_access_token
            del graph
        del msg
        del group_id
        del post
        del opt
    except Exception as err5:
        status3, err_msg3 = update_log(str(err5), 'Error Origin: Send FB Group Script')
        write_html('\nError Occurred while executing Scripts!!' + '\n' + status3)
        del err5
        del status3
        del err_msg3


write_html('Automated Script Started!\nThis will check for Cancelled Lectures and ATS Notifications every 5 minutes' + '\nPress <Ctrl-C> to stop thread.\n')
while True:
    try:
        actual_time = time.strftime("%H:%M")
        actual_time_min = time.strftime("%M")
        if actual_time_min in time_to_check[:6]:
            check_lectures()
        elif actual_time_min in time_to_check[6:]:
            check_ats()
        elif actual_time == "17:59":
            write_html("Closing Script! (School Closed)")
            exit()
        else:
            # write_html('Time: ' + actual_time)
            continue
        time.sleep(1)
        while time.strftime("%S") != "00":
            time.sleep(1)
        del actual_time
    except KeyboardInterrupt:
        write_html("Keyboard interrupt - waiting for thread to finish...")
        exit("Keyboard interrupt - waiting for thread to finish...")
    except Exception as err:
        status, err_msg = update_log(str(err), 'Error Origin: Timer to Execute Script')
        write_html('\nError Occurred while executing Scripts!!' + '\n' + status)
        del err
        del status
        del err_msg
