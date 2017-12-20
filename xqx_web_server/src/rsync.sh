#cd  /home/fqy188/workspace/qdcloud_web
# sudo mount -t vboxsf xqx_src /mnt/QdShare
cd  /mnt/QdShare/web
while [ 1=1 ]
do
rsync -azvrlR ./static qding@10.39.249.186:/opt/cloud_talk/src/web/   --exclude=.idea --force 
rsync -azvrlR ./templates qding@10.39.249.186:/opt/cloud_talk/src/web/   --exclude=.idea --force 
#rsync -azvrlR ./static qding@10.39.249.222:/opt/cloud_talk/src/web/   --exclude=.idea --force 
sleep 2
done
