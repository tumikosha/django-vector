# docker pull ankane/pgvector
# /home/all/pgvector-storage -папка с общим доступом для всех юзеров
# chmod a+rwx /home/all/pgvector-storage
 docker run -p 5432:5432 -p 49838:49838  \
 --detach \
    --name pgv \
    -e POSTGRES_PASSWORD=postgres \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v /home/all/pgvector-storage:/var/lib/postgresql/data \
    ankane/pgvector
#
docker ps -a

# /var/lib/postgresql/pgvector-storage
#docker run -p 5432:5432  \
#    --name pgv \
#    -e POSTGRES_PASSWORD=postgres \
#    -e PGDATA=/var/lib/postgresql/data/pgdata \
#    -v /media/tumi/nvme/pgvector-storage/:/var/lib/postgresql/data \
#    ankane/pgvector
#
#-v /custom/mount:/var/lib/postgresql/data \

 #--name some-postgres \
 #	-e POSTGRES_PASSWORD=mysecretpassword \
 #	-e PGDATA=/var/lib/postgresql/data/pgdata \


