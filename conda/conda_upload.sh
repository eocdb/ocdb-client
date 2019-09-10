# Only need to change these two variables
PKG_NAME=ocdb
USER=ocdb

mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export VERSION=0.1.1
conda build recipe
anaconda -t ${CONDA_UPLOAD_TOKEN} upload  -u ${USER} ${CONDA_BLD_PATH}/noarch/${PKG_NAME}-${VERSION}-0.tar.bz2 --force