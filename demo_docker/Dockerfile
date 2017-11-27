FROM ubuntu 

LABEL authors="Maarten Vermeyen, Koen Van Daele" 	

# system packages
RUN apt-get update && apt-get install -y \
    sudo \
    npm \
    git \
    curl \
    wget \
    libpq-dev \
    python-pip

WORKDIR /usr/local/src

# install hdt-cpp

RUN cd /usr/local/src && \
    git clone https://github.com/rdfhdt/hdt-cpp.git && \
    apt-get update && apt-get -y install \
    autoconf \
    build-essential \
    libraptor2-dev \
    libtool \
    liblzma-dev \
    liblzo2-dev \
    zlib1g-dev


# Install more recent serd
RUN wget https://github.com/drobilla/serd/archive/v0.28.0.tar.gz && \
    tar -xvzf *.tar.gz && \
    rm *.tar.gz && \
    cd serd-* && \
    ./waf configure && \
    ./waf && \ 
    ./waf install

# Install HDT tools
RUN cd hdt-cpp && \ 
    ./autogen.sh && \
    ./configure && \
    make -j2

# Expose binaries
ENV PATH /usr/local/src/hdt-cpp/hdt-lib/tools:$PATH

# reset WORKDIR
WORKDIR /
 
# install bower
RUN sudo npm install -g bower
RUN ln -s /usr/bin/nodejs /usr/bin/node

# install atramhasis
RUN pip install --upgrade pip && pip install atramhasis

RUN pcreate -s atramhasis_demo /opt/atramhasis_demo && \
    cd /opt/atramhasis_demo && \
    sed -i '/app:main/a atramhasis.dump_location = %(here)s/datadumps' development.ini && \
    pip install -r requirements-dev.txt && \
    python setup.py develop && \
    cd atramhasis_demo/static && \
    bower --allow-root install && \
    cd admin && \
    bower install --allow-root && \ 
    cd ../../.. && \
    alembic upgrade head && \
    initialize_atramhasis_db development.ini && \
    python setup.py compile_catalog && \
    dump_rdf development.ini

RUN cd /opt/atramhasis_demo && \
    sed -i '/app:main/a atramhasis.rdf2hdt = /usr/local/src/hdt-cpp/hdt-lib/tools/rdf2hdt' development.ini && \
    generate_ldf_config development.ini && \
    npm install -g ldf-server

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

COPY atramhasis.conf /opt/atramhasis.conf
EXPOSE 6543

CMD supervisord -c /opt/atramhasis.conf
