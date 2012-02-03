OpenShift - A sample TODO app using pyramids
============================================

This example has been taken from:

  http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/single_file_tasks/single_file_tasks.html

This repository is designed to be used with http://openshift.redhat.com/
applications. To use it, just follow the quickstart below.

Quickstart
==========

1) Create an account at http://openshift.redhat.com/
2) Create a wsgi-3.2 application and attach mysql to it:
    $ rhc-create-app -a reviewboard -t wsgi-3.2
    $ rhc-ctl-app -a reviewboard -e add-mysql-5.1
3) Add this upstream reviewboard repo
    $ cd reviewboard
    $ git remote add upstream -m master git://github.com/openshift/reviewboard-example.git
    $ git pull -s recursive -X theirs upstream master
4) Then push the repo upstream
    $ git push
5) That's it, you can now checkout your application at:
    http://reviewboard-$yourlogin.rhcloud.com
6) Default Admin Username: Admin
   Default Password: OpenShiftAdmin
