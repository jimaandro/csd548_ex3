1. _The example for autoscaling is available at GitHub (https\://github.com/chazapis/hy548). Improve it so that:_

1) _Instead of "Hello from Python Flask!", the flask-hello container will return the value of the MESSAGE environment variable when someone uses the service (use Python's os.getenv). Provide the new Dockerfile and hello.py. Build and upload the new container to Docker Hub._

_The new hello.py is:_

from flask import Flask

import os

app = Flask(\_\_name\_\_)

@app.route('/')

def index():

    message = os.getenv("MESSAGE", "Hello from Python Flask!")

    return message

if \_\_name\_\_ == "\_\_main\_\_":

    app.run(host='0.0.0.0', port=8080)

The Dockerfile is the same

FROM python:3.10.3-slim

RUN pip install Flask==2.0.3

COPY . /app

WORKDIR /app

CMD python hello.py

**To Build and upload we use these commands:**

    docker build -t flask-hello .
    docker login
    docker tag flask-hello jimaandron/flask-hello:latest
    docker push jimaandron/flask-hello:latest

1. _Provide two YAMLs to deploy the above container with all necessary resources (Deployment, Service, Ingress), so that "This is the first service!" is returned when someone visits the /first endpoint, and "This is the second service!" when someone visits the /second._

_Provide the commands needed to test the above two services with minikube (from running minikube, to curl or wget commands to use the services). Assume that the first deployment is in first.yaml and the second in second.yaml._

**The first yaml is this:**

apiVersion: networking.k8s.io/v1

kind: Ingress

metadata:

  name: first-ingress

spec:

  rules:

  - http:

      paths:

      - path: /first

        pathType: Prefix

        backend:

          service:

            name: first

            port:

              number: 8080

\---

apiVersion: v1

kind: Service

metadata:

  name: first

spec:

  type: ClusterIP

  ports:

  - port: 8080

  selector:

    app: first

\---

apiVersion: apps/v1

kind: Deployment

metadata:

  name: first

spec:

  replicas: 1

  selector:

    matchLabels:

      app: first

  template:

    metadata:

      labels:

        app: first

    spec:

      containers:

      - name: first

        image: jimaandron/flask-hello:1

        env:

        - name: MESSAGE

          value: "This is the first service!"

        resources:

          limits:

            cpu: "200m"

            memory: "128Mi"

**The second yaml is:**

apiVersion: networking.k8s.io/v1

kind: Ingress

metadata:

  name: second-ingress

spec:

  rules:

  - http:

      paths:

      - path: /second

        pathType: Prefix

        backend:

          service:

            name: second

            port:

              number: 8080

\---

apiVersion: v1

kind: Service

metadata:

  name: second

spec:

  type: ClusterIP

  ports:

  - port: 8080

  selector:

    app: second

\---

apiVersion: apps/v1

kind: Deployment

metadata:

  name: second

spec:

  replicas: 1

  selector:

    matchLabels:

      app: second

  template:

    metadata:

      labels:

        app: second

    spec:

      containers:

      - name: second

        image: jimaandron/flask-hello:1

        env:

        - name: MESSAGE

          value: "This is the second service!"

        resources:

          limits:

            cpu: "200m"

            memory: "128Mi"

**In both yamls we use the jimaandron/flask-hello:1 which we created before and we set message variable.**

_C. Provide the commands needed to test the above two services with minikube (from running minikube, to curl or wget commands to use the services). Assume that the first deployment is in first.yaml and the second in second.yaml._

**We need to apply the yamls**

    kubectl apply -f first.yaml
    kubectl apply -f second.yaml

**Then to get the IP and create tunnel, we run**

    minikube ip 
    minikube tunnel

**And then this to curl first and second sites.**

    curl http://IP/first
    curl http://IP/second

_2 Following on from the previous exercise, extend the YAML that implements the /first endpoint:_

1. _To limit each Pod to a maximum of 20% CPU and 256MB RAM._

1) _With a HorizontalPodAutoscaler manifest, which will increase the number of Pods in the Deployment when the average CPU usage exceeds 80%. Set a minimum of 1 Pod and a maximum of 8 for the Deployment._

**The new first.yaml is this now:**

apiVersion: networking.k8s.io/v1

kind: Ingress

metadata:

  name: first-ingress

spec:

  rules:

  - http:

      paths:

      - path: /first

        pathType: Prefix

        backend:

          service:

            name: first

            port:

              number: 8080

\---

apiVersion: v1

kind: Service

metadata:

  name: first

spec:

  type: ClusterIP

  ports:

  - port: 8080

  selector:

    app: first

\---

apiVersion: apps/v1

kind: Deployment

metadata:

  name: first

spec:

  replicas: 1

  selector:

    matchLabels:

      app: first

  template:

    metadata:

      labels:

        app: first

    spec:

      containers:

      - name: first

        image: jimaandron/flask-hello:latest

        env:

        - name: MESSAGE

          value: "This is the first service!"

        resources:

          limits:

            cpu: "200m"

            memory: "256Mi"   # Limiting each Pod to a maximum of 256MB RAM

\---

apiVersion: autoscaling/v2beta2

kind: HorizontalPodAutoscaler

metadata:

  name: first-hpa

spec:

  scaleTargetRef:

    apiVersion: apps/v1

    kind: Deployment

    name: first

  minReplicas: 1

  maxReplicas: 8

  metrics:

  - type: Resource

    resource:

      name: cpu

      targetAverageUtilization: 80

_Run some http benchmark to find the maximum requests per second both services can handle, using 1 or 100 simultaneous clients. At how many containers does the scaling of the first service stop? Provide the new YAML, the test results, and a screenshot of the tool you used, or its output if it was a command line utility._

**Then we run** 

    ab -n 1000 -c 1 http://192.168.49.2/first

**But since I have Windows I will run this inside another docker container** 

    docker run --rm -it --name ab-container httpd:2.4 ab -n 1000 -c 1 http://192.168.49.2/first

**I had some problems with Windows.. so I couldn’t get measures. Windows are outdated due to a bug, which I couldn’t fix. And due to outdated Windows, docker doesn’t run in latest version.**

_3 If you have enabled the ingress addon in minikube, remove it. Issue the commands to install the Ingress controller implemented with Nginx using Helm. You will find the chart at https\://artifacthub.io/packages/helm/ingress-nginx/ingress-nginx. Try again the services of the above exercises. What changes are needed in the YAML files to make them work (if any)?_

**First we disable the ingress**

    minikube addons disable ingress

**Then we install Ingress controller implemented with Nginx using Helm**

**But we use Windows, so I have to install Helm first through** [**https://community.chocolatey.org/packages/kubernetes-helm**](https://community.chocolatey.org/packages/kubernetes-helm) ****

**And then**

`helm repo add ingress-nginx `[`https://kubernetes.github.io/ingress-nginx`](https://kubernetes.github.io/ingress-nginx) ****

**Then we update the repo and we install the ingress**

    helm repo update
    helm install nginx-ingress ingress-nginx/ingress-nginx

**we need to change the Ingress part in any yaml like this:**

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: flask-ingress
      annotations:
        kubernetes.io/ingress.class: "nginx"
        nginx.ingress.kubernetes.io/rewrite-target: /
    spec:
      rules:
      - http:
          paths:
          - path: /first
            pathType: Prefix
            backend:
              service:
                name: flask
                port:
                  number: 8080

4. _Create a Helm chart for the service that implements the /first endpoint of exercise 2. The chart should define variables for:_

1) _The string to return._

1. _The endpoint to use for the service._

1) _The CPU and memory limits of each Pod (optional, default is no limits)._

1. _The maximum number of Deployment Pods for the HorizontalPodAutoscaler (optional, default is 10)._

_Provide the chart files and the commands needed to install a service named "third" that will reply "This is a third service!", use the /third endpoint, be limited to 25% CPU (no memory limit), and scale automatically up to 20 Pods via the HorizontalPodAutoscaler._

**First we create the Helm Chart** 

    helm create third-service

**Then in a yaml we create the the variables we need** 

    # String to return
    message: "This is a third service!"

    # Endpoint for the service
    endpoint: "/third"

    # CPU and memory limits for each Pod (optional, default is no limits)
    cpuLimit: "25m"
    memoryLimit: ""

    # Maximum number of Deployment Pods for HorizontalPodAutoscaler (optional, default is 10)
    maxReplicas: 20

**Then we create the third.yaml and then run**

    helm install third ./third-service
    cd third-service

    helm install third . --set message="This is a third service!",endpoint="/third",cpuLimit="25m",maxReplicas=20
