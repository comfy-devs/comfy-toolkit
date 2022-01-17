# Stage: build
FROM archlinux:latest
RUN pacman --noconfirm -Syu

# Create new user (build)
RUN useradd --shell=/bin/bash build
RUN echo "build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Build FFmpeg
RUN pacman --noconfirm -S base-devel wget git libfdk-aac 

WORKDIR /tmp
USER build
RUN mkdir -p ffmpeg-git
RUN cd ffmpeg-git && wget -O 010-ffmpeg-fix-vmaf-model-path.patch "https://aur.archlinux.org/cgit/aur.git/plain/010-ffmpeg-fix-vmaf-model-path.patch?h=ffmpeg-git"
RUN cd ffmpeg-git && wget -O PKGBUILD "https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=ffmpeg-git"
RUN cd ffmpeg-git && sed -i 's/--enable-version3/--enable-version3 --enable-nonfree --enable-libfdk-aac/' PKGBUILD
RUN cd ffmpeg-git && makepkg --noconfirm -si
USER root

# Build src
RUN pacman --noconfirm -S nodejs yarn bc libwebp

WORKDIR /usr/src/app
COPY . .
RUN cd src/clean-vtt && yarn && yarn run build

# Install extra packages
RUN pacman --noconfirm -S neovim ranger

# Stage: run
WORKDIR /usr/src/app/src/scripts
CMD [ "ffmpeg", "-version" ]