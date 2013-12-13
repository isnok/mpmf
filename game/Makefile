# A collection of useful oneliners

LOGTO = /tmp/game

clean:
	find . -type f \( -name "*.pyc" -or -name "dropin.cache" \) -exec rm {} \;


serve: clean
	ps fax | grep -v grep | grep -q 'serve\.py' || { ./serve.py -l $(LOGTO)_server.log & }

watch:
	tail -F /tmp/game_server.log

stop:
	kill `ps fax | awk '/serve\.py/{print $$1;}'`

ascii: serve
	./play.py -a -l $(LOGTO)_ascii.log || cat $(LOGTO)_ascii.log && tail -n 20 $(LOGTO)_ascii.log
	@echo "===> Server still runnning. To stop it you can use the 'stop' target."

sdl: serve
	./play.py
	@echo "===> Server still runnning. To stop it you can use the 'stop' target."

deb-deps:
	sudo apt-get install python-twisted python-pygame python-stdlib

build-deps:
	#pygame
	sudo apt-get install python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev  libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev
	pip install pygame Twisted
	cd /usr/include/linux; sudo ln -s ../libv4l1-videodev.h videodev.h

optional-deps:
	sudo apt-get install tree

tree: clean
	tree
