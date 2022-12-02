# Stage: build
FROM archlinux:base-20221127.0.105785

# Create new user (build)
RUN useradd --shell=/bin/bash build
RUN echo "build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Build vmaf-git
USER root
RUN pacman --noconfirm -Syu gcc-libs doxygen git meson nasm vim
RUN pacman --noconfirm -Sy base-devel wget
USER build
WORKDIR /tmp

RUN mkdir -p vmaf-git
RUN cd vmaf-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=vmaf-git"
RUN cd vmaf-git && makepkg --noconfirm -si

# Build FFmpeg
USER root
RUN pacman --noconfirm -Sy libfdk-aac
USER build
WORKDIR /tmp

RUN mkdir -p ffmpeg-git
RUN cd ffmpeg-git && wget -O 040-ffmpeg-add-av_stream_get_first_dts-for-chromium.patch "https://aur.archlinux.org/cgit/aur.git/plain/040-ffmpeg-add-av_stream_get_first_dts-for-chromium.patch?h=ffmpeg-git"
RUN cd ffmpeg-git && wget -O 060-ffmpeg-fix-segfault-with-avisynthplus.patch "https://aur.archlinux.org/cgit/aur.git/plain/060-ffmpeg-fix-segfault-with-avisynthplus.patch?h=ffmpeg-git"
RUN cd ffmpeg-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=ffmpeg-git"
RUN cd ffmpeg-git && sed -i 's/--enable-version3/--enable-version3 --enable-nonfree --enable-libfdk-aac/' PKGBUILD
RUN cd ffmpeg-git && makepkg --noconfirm -si

# Install required packages
USER root
RUN pacman --noconfirm -Sy python python-pip nodejs yarn bc jq libwebp openssh rsync imagemagick ranger transmission-cli
WORKDIR /usr/src/app

# Install extra packages
RUN pacman --noconfirm -Sy neovim

# Build src
COPY . .
RUN cd src/dashboard && pip install -r requirements.txt
RUN cd src/clean-vtt && yarn
RUN cd src/clean-vtt && yarn run build && yarn remove $(cat package.json | jq -r '.devDependencies | keys | join(" ")')
RUN cd src/create-torrent && yarn
RUN cd src/create-torrent && yarn run build && yarn remove $(cat package.json | jq -r '.devDependencies | keys | join(" ")')
RUN cd src/create-torrent && sed -i 's/flat()/flat(64)/' node_modules/create-torrent/get-files.js

# Stage: run
WORKDIR /usr/src/app/src/dashboard
CMD [ "ffmpeg", "-version" ]