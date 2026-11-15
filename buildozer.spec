[app]
title = CONVERTER
package.name = converter
package.domain = org.converter
source.dir = .
source.include_exts = py,png,ttf
version = 1.0
requirements = python3,kivy==2.3.0,pyjnius,android,androidstorage4kivy
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/assets/icon.png
android.presplash_color = #FFFFFF
android.api = 33
android.ndk = 25b
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
