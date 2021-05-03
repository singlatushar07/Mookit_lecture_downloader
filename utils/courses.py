from bs4 import BeautifulSoup as bs


def getCourseList(url, session):
    request = session.get(url)
    soup = bs(request.content, "lxml")
    courses = soup.find_all(lambda tag: tag.name ==
                            'a' and tag["href"].startswith("https://hello.iitk.ac.in/course"))
    courseList = []
    for i in range(len(courses)):
        courseList.append({
            "name": courses[i].findChild("h3").get_text(),
            "courseCode": courses[i]['href'].rsplit('/', 1)[-1]
        })

    return courseList


def getCourseContent(index, courseList, session):
    url = "https://hello.iitk.ac.in/api/" + \
        courseList[index]['courseCode'] + "/lectures/summary"
    r = session.get(url)
    r = r.json()
    contents = []
    for content in r:
        # videoUrl = [links['path'] for links in content['videosUploaded']
        #             if links['type'] == 'original']
        data = {
            'week': content['week'],
            'title': content['title'],
            'topic': content['topic'],
            'videoUrl': content['videosUploaded'],
            'resources': content['resources']
        }
        contents.append(data)
    return contents
