

# Dependencies are

+ plumbum
+ requests 1.1.0 (do ```sudo pip install requests==1.1.0```)
+ python-firebase
+ Jinja2

You need to have a backup of the hosts file or you could mess up your computer, so run

```sudo cp /etc/hosts /etc/hosts.backup```

Now you can run ```sudo app.py``` and it will start up a web server and pull the latest data off Firebase
