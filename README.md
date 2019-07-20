# cloud-pine: The alternative for Cloud9 PRO (just for me!)

http://yusukeiwaki.hatenablog.com/entry/2019/07/13/my-cloud9-alternative

# Setup

## マシンを２，３台用意

dockerを入れる。

```
curl https://raw.githubusercontent.com/YusukeIwaki/cloud-pine/master/install-docker-ce.sh | bash
```

docker swarmでクラスタを組む。

## network作成

```
docker network create --driver overlay --internal cloud-pine-master
```

## リバースプロキシのデプロイ


```
cd reverse_proxy
docker stack deploy --compose-file docker-compose.yml reverse_proxy
```

## ワークスペースの追加

```
cd workspace
docker stack deploy --compose-file docker-compose.yml playground1
```

→ playground1.ide.c9work.net でCloud9ワークスペースが使用可能になる
→ ワークスペースの8080番ポートで公開されたものが playground1.preview.c9work.netで見れる

## ワークスペースの削除

```
docker stack rm playground2
DOCKER_HOST=ssh://c9work-slave1 docker volume rm playground2_workspace-data # docker service ps でノードを予め特定しておく必要あり。
```
