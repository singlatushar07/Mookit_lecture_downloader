from utils.courses import getCourseList, getCourseContent
from utils.login import login, updateHeader
from urllib.parse import unquote
import wget
import requests
import pickle
import os
from tabulate import tabulate
from unsilence import Unsilence


loginUrl = "https://hello.iitk.ac.in/user/login"
courseListUrl = "https://hello.iitk.ac.in/courses/"

s = requests.session()

cookieFile = os.path.join(os.path.dirname(__file__), './data/cookie')
if(not os.path.exists(cookieFile)):
    s = login(loginUrl)
    with open(cookieFile, 'wb') as f:
        pickle.dump(s.cookies, f)
else:
    with open(cookieFile, 'rb') as f:
        s.cookies.update(pickle.load(f))

try:
    s = updateHeader(s)
except:
    print("Login Failed")
    if(os.path.exists(cookieFile)):
        os.remove(cookieFile)
    exit()


courseList = getCourseList(courseListUrl, s)
# print(courseList)
print("You are enrolled in the following courses:")
print("No.  Course Name")
for i, course in enumerate(courseList):
    print(i+1, "  " + course['name'])

index = int(input("Enter the No of course you want to download content: "))
index -= 1
lectures = getCourseContent(index, courseList, s)
temp = []
for lecture in lectures:
    temp.append([lecture['week'], lecture['title'], lecture['topic'], len(
        lecture['videoUrl']) > 0, len(lecture['resources']) > 0])

print()
print("Found following " + str(len(temp)) + " resources")
print(tabulate(temp, headers=["Week", "Title", "Topic",
                              "Video Lecture Availiable", "Additional Resorces Availiable"]))

downloadQuality = input(
    "Enter video quality you want to download(mp4 or original): ")

wantSilence = input(
    "Do you want to remove silenced parts from the downloaded videos? (yes/no) ")

downloadPath = os.path.join(os.path.dirname(
    __file__), './data/' + courseList[index]['courseCode'] + '/')
if not os.path.exists(downloadPath):
    os.makedirs(downloadPath)

failed = []
success = []
for lecture in lectures:
    print("Downloading %s" % lecture['title'])
    downloadPath = os.path.join(os.path.dirname(
        __file__), './data/' + courseList[index]['courseCode'] + '/' + lecture['week'] + '/')
    if not os.path.exists(downloadPath):
        os.makedirs(downloadPath)

    file_name = os.path.join(os.path.dirname(
        __file__), './data/' + courseList[index]['courseCode'] + '/' + lecture['week'] + '/' + lecture['title'] + ".mp4")
    flag = 0
    for video in lecture['videoUrl']:
        if(os.path.exists(file_name)):
            if(video['type'] == downloadQuality):
                success.append(file_name)
            continue
        try:
            if(video['type'] == downloadQuality):
                videoUrl = unquote(video['path'])
                wget.download(videoUrl, out=file_name)
                success.append(file_name)
        except:
            failed.append(lecture['title'])
            print("Failed to Download " + lecture['title'])

    for resourceFile in lecture['resources']:
        file_name = os.path.join(os.path.dirname(
            __file__), './data/' + courseList[index]['courseCode'] + '/' + lecture['week'] + '/' + resourceFile['fileName'])
        if(os.path.exists(file_name)):
            continue
        wget.download(unquote(resourceFile['fileURL']), out=file_name)
    print()
    print("%s downloaded!\n" % file_name)

if(len(failed) > 0):
    print("Following files were not downloaded")
    for i in failed:
        print(i)

wantSilence = input(
    "Do you want to remove silenced parts from the downloaded videos? (yes/no) ")
if(wantSilence == "yes"):
    print("The operation may take while. Sit back and relax. You can always resume by rerunning the program")
    # print(success)
    for video in success:
        print("Processing", video)
        output_file = video[:-4]+"_silenced.mp4"
        if(os.path.exists(output_file)):
            print("The file", output_file, "is already processed.")
            continue
        u = Unsilence(video)
        # print(video[:-4]+"_silenced.mp4")
        u.detect_silence()

        estimated_time = u.estimate_time(
            audible_speed=1, silent_speed=100)

        u.render_media(video[:-4]+"_silenced.mp4", audible_speed=1,
                       silent_speed=100)
        print(video[:-4]+"_silenced.mp4", "processed")
        print()
