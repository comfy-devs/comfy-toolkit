# Stage: build
FROM archlinux:base-devel-20230108.0.116909

# Create new user (build)
RUN useradd --shell=/bin/bash build
RUN echo "build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Build vmaf-git
USER root
RUN pacman --noconfirm -Syu doxygen git meson nasm wget
USER build
WORKDIR /tmp

RUN mkdir -p vmaf-git
RUN cd vmaf-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=vmaf-git"
RUN cd vmaf-git && makepkg --noconfirm -si

# Build FFmpeg
USER root
RUN pacman --noconfirm -Syu libfdk-aac
USER build
WORKDIR /tmp

RUN mkdir -p ffmpeg-git
RUN cd ffmpeg-git && wget -O 040-ffmpeg-add-av_stream_get_first_dts-for-chromium.patch "https://aur.archlinux.org/cgit/aur.git/plain/040-ffmpeg-add-av_stream_get_first_dts-for-chromium.patch?h=ffmpeg-git"
RUN cd ffmpeg-git && wget -O 060-ffmpeg-fix-segfault-with-avisynthplus.patch "https://aur.archlinux.org/cgit/aur.git/plain/060-ffmpeg-fix-segfault-with-avisynthplus.patch?h=ffmpeg-git"
RUN cd ffmpeg-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=ffmpeg-git"
RUN cd ffmpeg-git && sed -i 's/--enable-version3/--enable-version3 --enable-nonfree --enable-libfdk-aac/' PKGBUILD
RUN cd ffmpeg-git && makepkg --noconfirm -si

# Install python
USER root
RUN pacman --noconfirm -Syu python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install required packages (and extra useful ones)
RUN pacman --noconfirm -Syu nodejs yarn bc jq libwebp openssh rsync imagemagick ranger transmission-cli neovim

# Build node utility packages
WORKDIR /usr/src/app
COPY src/clean-vtt src/clean-vtt
COPY src/create-torrent src/create-torrent
RUN cd src/clean-vtt && yarn
RUN cd src/clean-vtt && yarn run build && yarn remove $(cat package.json | jq -r '.devDependencies | keys | join(" ")')
RUN cd src/create-torrent && yarn
RUN cd src/create-torrent && yarn run build && yarn remove $(cat package.json | jq -r '.devDependencies | keys | join(" ")')
RUN cd src/create-torrent && sed -i 's/flat()/flat(64)/' node_modules/create-torrent/get-files.js

# Prepare python dashboard
WORKDIR /usr/src/app
COPY src/dashboard/requirements.txt src/dashboard/requirements.txt
RUN cd src/dashboard && pip3 install -r requirements.txt
COPY src/dashboard src/dashboard
COPY src/scripts src/scripts

# Stage: run
WORKDIR /usr/src/app/src/dashboard
CMD [ "ffmpeg", "-version" ]