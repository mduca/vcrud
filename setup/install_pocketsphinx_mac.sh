 git clone https://github.com/cmusphinx/pocketsphinx.git
 brew install cmu-pocketsphinx
 brew install swig
 pip3 install --upgrade pip setuptools wheel
 brew install openal-soft
 cd /usr/local/include
 ln -s /usr/local/Cellar/openal-soft/1.20.1/include/AL/* .
 pip3 install pocketsphinx
