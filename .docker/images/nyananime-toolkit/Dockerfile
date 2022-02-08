# Stage: build
FROM archlinux:latest
RUN pacman --noconfirm -Syu

# Create new user (build)
RUN useradd --shell=/bin/bash build
RUN echo "build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Build vmaf-git
USER root
RUN pacman --noconfirm -S git base-devel wget
USER build
WORKDIR /tmp

RUN mkdir -p vmaf-git
RUN cd vmaf-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=vmaf-git"
RUN cd vmaf-git && makepkg --noconfirm -si

# Build FFmpeg
USER root
RUN pacman --noconfirm -S libfdk-aac
USER build
WORKDIR /tmp

RUN mkdir -p ffmpeg-git
RUN cd ffmpeg-git && wget -O 010-ffmpeg-add-av_stream_get_first_dts-for-chromium.patch "https://aur.archlinux.org/cgit/aur.git/plain/010-ffmpeg-add-av_stream_get_first_dts-for-chromium.patch?h=ffmpeg-git"
RUN cd ffmpeg-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=ffmpeg-git"
RUN cd ffmpeg-git && sed -i 's/--enable-version3/--enable-version3 --enable-nonfree --enable-libfdk-aac/' PKGBUILD
RUN cd ffmpeg-git && makepkg --noconfirm -si

# Build src
USER root
RUN pacman --noconfirm -S python python-pip nodejs yarn bc libwebp
WORKDIR /usr/src/app

COPY . .
RUN cd src/clean-vtt && yarn && yarn run build

# Install extra packages
RUN pacman --noconfirm -S neovim ranger

# Stage: run
WORKDIR /usr/src/app/src/scripts
CMD [ "ffmpeg", "-version" ]