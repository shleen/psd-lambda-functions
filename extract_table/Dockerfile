FROM public.ecr.aws/lambda/python@sha256:7f867f958f685d4321e4520e20b13900a47210ee57b3e41d05395b11f4c93c70 as build
FROM public.ecr.aws/lambda/python@sha256:7f867f958f685d4321e4520e20b13900a47210ee57b3e41d05395b11f4c93c70
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y
RUN pip install pdfplumber
RUN pip install pandas
RUN pip install openpyxl
RUN pip install python-dotenv
RUN pip install boto3
COPY main.py ./
CMD [ "main.handler" ]
