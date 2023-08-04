FROM public.ecr.aws/lambda/python@sha256:7f867f958f685d4321e4520e20b13900a47210ee57b3e41d05395b11f4c93c70 as build
ENV PATH="$PATH:/opt"
RUN unset SNAP_NAME
RUN unset SNAP_INSTANCE_NAME
RUN yum install -y unzip tar gzip wget bzip2 firefox && \
    curl -Lo "/tmp/geckodriver-v0.33.0-linux64.tar.gz" "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz" && \
    tar -xvzf /tmp/geckodriver-v0.33.0-linux64.tar.gz -C /opt/ 
# FIXME: don't know how to install firefox. now using yum to install but still doesn't work.
RUN wget "https://download.mozilla.org/?product=firefox-latest&os=linux&lang=pt-BR" -O firefox.tar.bz2
RUN tar -jxvf  firefox.tar.bz2 -C /opt/

FROM public.ecr.aws/lambda/python@sha256:7f867f958f685d4321e4520e20b13900a47210ee57b3e41d05395b11f4c93c70
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y
RUN pip install selenium==4.9.1
RUN pip install pandas
RUN pip install python-dotenv
RUN pip install openpyxl
RUN pip install boto3

# Copy from build stage to the directory within the current Docker image being built
COPY --from=build /opt/geckodriver /opt/
# FIXME:
COPY --from=build /opt/firefox /opt/firefox

COPY main.py ./
CMD [ "main.handler" ]