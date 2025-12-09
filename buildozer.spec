[app]
title = Modem Rebooter
package.name = modemrebooter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,urllib3,chardet,idna,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.private_storage = True
android.logcat_filters = *:S python:D
android.debug_artifact = apk
android.manifest.application_attributes = android:usesCleartextTraffic="true"
p4a.branch = master
# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
