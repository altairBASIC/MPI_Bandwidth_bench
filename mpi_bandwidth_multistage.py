# Base de la imagen
Stage0 += baseimage(image='centos:7.6.1810', _as='build')

# Cambiar repositorios y actualizar
Stage0 += shell(commands=[
    'sed -i "s|^mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-Base.repo',
    'sed -i "s|^#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-Base.repo',
    'yum clean all',
    'yum makecache',
    'yum install -y epel-release gcc gcc-c++ make wget libgomp bzip2',  
    'rm -rf /var/cache/yum/*'
])

# Repositorio y dependencias de Mellanox
Stage0 += shell(commands=[
    'rpm --import https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox',
    'yum install -y yum-utils',
    'yum-config-manager --add-repo https://linux.mellanox.com/public/repo/mlnx_ofed/4.5-1.0.1.0/rhel7.2/mellanox_mlnx_ofed.repo',
    'yum install -y libibmad libibmad-devel libibumad libibumad-devel libibverbs libibverbs-devel libibverbs-utils libmlx4 libmlx4-devel libmlx5 libmlx5-devel librdmacm librdmacm-devel',
    'rm -rf /var/cache/yum/*'
])

# Instalar OpenMPI
Stage0 += shell(commands=[
    'mkdir -p /var/tmp',
    'wget -q -nc --no-check-certificate -P /var/tmp https://www.open-mpi.org/software/ompi/v3.1/downloads/openmpi-3.1.2.tar.bz2',
    'tar -x -f /var/tmp/openmpi-3.1.2.tar.bz2 -C /var/tmp -j',
    'cd /var/tmp/openmpi-3.1.2',
    './configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-orterun-prefix-by-default --with-verbs --without-cuda',
    'make -j$(nproc)',
    'make install',
    'rm -rf /var/tmp/openmpi-3.1.2 /var/tmp/openmpi-3.1.2.tar.bz2'
])

# Configurar variables de entorno
Stage0 += environment(variables={
    'LD_LIBRARY_PATH': '/usr/local/openmpi/lib:$LD_LIBRARY_PATH',
    'PATH': '/usr/local/openmpi/bin:$PATH'
})

# Copiar y compilar el codigo mpi_bandwidth.c
Stage0 += copy(src='sources/mpi_bandwidth.c', dest='/var/tmp/mpi_bandwidth.c')
Stage0 += shell(commands=['mpicc -o /usr/local/bin/mpi_bandwidth /var/tmp/mpi_bandwidth.c'])
