FROM archlinux
RUN pacman -Syyu --noconfirm
RUN pacman -S git gcc make python python-pip openmpi --noconfirm
RUN pip install pyaml pycparser
RUN useradd -m sombrero
RUN mkdir /output && chown sombrero /output
COPY bootstrap.sh /home/sombrero
RUN chown sombrero /home/sombrero/bootstrap.sh
RUN pacman -S bc --noconfirm
USER sombrero
RUN chmod +x /home/sombrero/bootstrap.sh
WORKDIR /home/sombrero
CMD [ "./bootstrap.sh" ]
