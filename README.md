# alertmanager-dingtalk-hook :lemon: :tangerine: :cherries: :cake: :grapes: :watermelon: :strawberry: :corn: :peach:
AlertManager 钉钉报警简单服务示例

![alertmanager dingtalk message demo](https://www.qikqiak.com/k8s-book/docs/images/alertmanager-dingtalk-message.png)

## 运行
### 使用`Docker`运行
```shell
$ docker run -p 5000:5000 --name -e ROBOT_TOKEN=<钉钉机器人TOKEN> dingtalk-hook -d cnych/alertmanager-dingtalk-hook:v0.2
```

### 在`Kubernetes`集群中运行
第一步建议将钉钉机器人TOKEN创建成`Secret`资源对象：
```shell
$ kubectl create secret generic dingtalk-secret --from-literal=token=<钉钉群聊的机器人TOKEN> -n kube-ops
secret "dingtalk-secret" created
```

然后定义`Deployment`和`Service`资源对象：(dingtalk-hook.yaml)
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: dingtalk-hook
  namespace: kube-ops
spec:
  template:
    metadata:
      labels:
        app: dingtalk-hook
    spec:
      containers:
      - name: dingtalk-hook
        image: cnych/alertmanager-dingtalk-hook:v0.1.3
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
          name: http
        env:
        - name: ROBOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: dingtalk-secret
              key: token
        resources:
          requests:
            cpu: 50m
            memory: 100Mi
          limits:
            cpu: 50m
            memory: 100Mi

---
apiVersion: v1
kind: Service
metadata:
  name: dingtalk-hook
  namespace: kube-ops
spec:
  selector:
    app: dingtalk-hook
  ports:
  - name: hook
    port: 5000
    targetPort: http
```

直接创建上面的资源对象即可：
```shell
$ kubectl create -f dingtalk-hook.yaml
deployment.extensions "dingtalk-hook" created
service "dingtalk-hook" created
$ kubectl get pods -n kube-ops
NAME                            READY     STATUS      RESTARTS   AGE
dingtalk-hook-c4fcd8cd6-6r2b6   1/1       Running     0          45m
......
```

最后在`AlertManager`中 webhook 地址直接通过 DNS 形式访问即可：
```yaml
receivers:
- name: 'webhook'
  webhook_configs:
  - url: 'http://dingtalk-hook.kube-ops.svc.cluster.local:5000'
    send_resolved: true
```

## 参考文档
* [钉钉自定义机器人文档](https://open-doc.dingtalk.com/microapp/serverapi2/qf2nxq)
* [AlertManager 的使用](https://www.qikqiak.com/k8s-book/docs/57.AlertManager%E7%9A%84%E4%BD%BF%E7%94%A8.html)

