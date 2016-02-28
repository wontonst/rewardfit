
# Rewardfit

*RewardFit is the project name and not the product name.*

## Dependencies

+ plumbum
+ requests 1.1.0 (do ```sudo pip install requests==1.1.0```)
+ python-firebase
+ Jinja2

Now you can run ```sudo app.py``` and it will start up a web server and tell you to authenticate through FitBit OAuth.

If website blocking works but doesn't show the RewardFit page, then delete ```~/Library/Cookies/HSTS.plist``` and then clear your cache. This will prevent the browser from defaulting to HTTPS.
