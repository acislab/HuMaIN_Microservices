#!/bin/sh
cd /opt
# The following line will take 30 minutes to install.
yum -y update 
yum -y install libstdc++ autoconf automake libtool autoconf-archive pkg-config gcc gcc-c++ make libjpeg-devel libpng-devel libtiff-devel zlib-devel wget
yum group install -y "Development Tools"


# Install Leptonica from Source
wget http://www.leptonica.com/source/leptonica-1.75.3.tar.gz
tar -zxvf leptonica-1.75.3.tar.gz
rm leptonica-1.75.3.tar.gz
cd leptonica-1.75.3
./autobuild
./configure
make -j
make install
cd ..

# Install Tesseract from Source
wget https://github.com/tesseract-ocr/tesseract/archive/4.0.0-beta.1.tar.gz
tar -zxvf 4.0.0-beta.1.tar.gz
rm 4.0.0-beta.1.tar.gz
cd tesseract-4.0.0-beta.1/
./autogen.sh
PKG_CONFIG_PATH=/usr/local/lib/pkgconfig LIBLEPT_HEADERSDIR=/usr/local/include ./configure --with-extra-includes=/usr/local/include --with-extra-libraries=/usr/local/lib
LDFLAGS="-L/usr/local/lib" CFLAGS="-I/usr/local/include" make -j
make install
ldconfig
cd ..

# Download and install tesseract language files (Tesseract 4 traineddata files)
wget https://github.com/tesseract-ocr/tessdata/raw/master/osd.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/master/equ.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/master/chi_sim.traineddata
# download another other languages you like
mv *.traineddata /usr/local/share/tessdata

yum clean all