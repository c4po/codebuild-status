from flask import Flask, render_template
import datetime
import pytz
import boto3

app = Flask(__name__)

client = boto3.client("codebuild")

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    return value.strftime(format)


def getProjects():
    list_response = client.list_projects(sortBy="NAME", sortOrder="ASCENDING")
    projects=[]
    while True:
        projects_detail = client.batch_get_projects(names = list_response["projects"])
        for project in projects_detail["projects"]:
            name = project["name"]
            default_branch = project["sourceVersion"]
            badge_info = project["badge"]["badgeRequestUrl"]
            badge_url = badge_info[0:badge_info.rfind("=")] + "=" + default_branch
            projects.append( {"name":name, "badge_url":badge_url})
        if "nextToken" in list_response:
            list_response = client.list_projects(
                sortBy="NAME", sortOrder="ASCENDING", nextToken=list_response["nextToken"]
            )
        else:
            break    
    return projects

@app.route("/")
def template_test():
    return render_template('template.html', projects=getProjects(), 
         title="Index", current_time=datetime.datetime.now(pytz.timezone("EST")))

if __name__ == '__main__':
    app.run()
