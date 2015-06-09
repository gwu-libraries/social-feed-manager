from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://')


@app.task
def user_timeline_task(args, options):
    f = open('taskout.txt','w')
    f.write("user_timeline_task ran!\n")
    f.close()
    print "this is the user_timeline_task"
