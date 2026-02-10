
# Train Ticket：A Benchmark Microservice System
# <img src="./image/logo.png">


The project is a train ticket booking system based on microservice architecture which contains 41 microservices. The programming languages and frameworks it used are as below.
- Java - Spring Boot, Spring Cloud
- Node.js - Express
- Python - Django
- Go - Webgo
- DB - Mongo、MySQL

You can get more details at [Wiki Pages](https://github.com/FudanSELab/train-ticket/wiki).

## Service Architecture Graph
![architecture](./image/2.png)

## Quick Start

Create Four ubuntu EC2 instances (t2.xlarge) in AWS
Connect the instances using security groups
Allow all traffic on 172.31.0.0/16 (Source) between instances.
Allow tcp port 22 (ssh) and 80 (http) on 0.0.0.0/0 (Source) to all instances.
Install MicroK8s and other tools on all the Instances

```
sudo apt update
sudo apt install git
sudo apt install gh
sudo apt install snapd -y
sudo snap install microk8s --classic
```

Check the status of MicroK8s and ensure it’s running:
```
microk8s status --wait-ready
```

Enable Ingress
```
 microk8s enable ingress
```

Add user to the MicroK8s group for easier access on all instances.
```
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
```

Logout and login back in to apply group changes.

Cluster Setup

Generate kubectl config on master node
```
microk8s config > ~/.kube/microk8s-config
```

Setting shell profile on master node

```
export KUBECONFIG=$HOME/.kube/microk8s-config
export KUBECONFIG=/home/ubuntu/.kube/microk8s-config
echo "export KUBECONFIG=$HOME/.kube/microk8s-config" >> ~/.bashrc
source ~/.bashrc
echo $KUBECONFIG
```

On the master node (node1), run:
```
microk8s add-node
```

On the first worker node (node2) get the output from the previous command and join node2 to master (node1)
```
microk8s join 172.31.0.0:25000/<X>/<Y> --worker
```

On the master node (node1), run this again:
```
microk8s add-node
```

On the second worker node (node3) get the output from the previous command and join node3 to master (node1)
```
microk8s join 172.31.0.0:25000/<X>/<Y> --worker
```

On the master node (node1), run this again:
```
microk8s add-node
```

On the third worker node (node4) get the output from the previous command and join node4 to master (node1)
```
microk8s join 172.31.0.0:25000/<X>/<Y> --worker
```

Ensure there are 4 nodes

microk8s kubectl get nodes -o wide

Add HashiCorp GPG key and install Terraform
```
sudo apt update
sudo apt install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install terraform
terraform version
```

Give role to the master and worker nodes
```
microk8s kubectl label node <ip-ip-address> role=node1
microk8s kubectl label node <ip-ip-address> role=node2
microk8s kubectl label node <ip-ip-address> role=node3
microk8s kubectl label node <ip-ip-address> role=node4
```

Clone train-ticket respository from master node in the cluster. Set if you are using a particular branch.
```
gh auth login
gh repo clone newrelic-forks/train-ticket -- --branch <branch>
cd train-ticket
```

Create namespace:
```
microk8s kubectl create namespace store
```

Run the configure script. It will ask for INGEST LICENSE KEY, USER KEY, ACCOUNT ID and REGION.
```
./configure
``` 

After successfully running the configure script, check the pods and services status.
```
microk8s kubectl -n store get pods -o wide
microk8s kubectl -n store get service -o wide
```

Verify Ingress Setup
```
microk8s kubectl -n store get ingress
```

You should see an output similar to this:
```
NAME               CLASS    HOSTS   ADDRESS     PORTS   AGE
all-ingress        public   *       127.0.0.1   80      7m12s
```

Now, you should be able to access the website at http://<public-ip>/ from anywhere on the internet using any public IP assigned to any AWS EC2 instance that was provisioned.

## Screenshot
![screenshot](./image/main_interface.png)
In order to know how to use the application, you can refer to [the User Guide](https://github.com/FudanSELab/train-ticket/wiki/User-Guide).

## Communication

* [FAQ](https://github.com/FudanSELab/train-ticket/wiki/FAQ)
* [Submit an issue](https://github.com/FudanSELab/train-ticket/issues)
* [Open a pull request](https://github.com/FudanSELab/train-ticket/pulls)

## Information

* [Release Note](https://github.com/FudanSELab/train-ticket/wiki/Release-Note)

## Serverless Train Ticket

We have released a serverless version of Train Ticket.

* [serverless-trainticket](https://github.com/FudanSELab/serverless-trainticket)

## Paper Reference
Bowen Li, Xin Peng, Qilin Xiang, Hanzhang Wang, Tao Xie, Jun Sun, Xuanzhe Liu. <br/>
**Enjoy your observability: an industrial survey of microservice tracing and analysis**<br/>
[Empirical Software Engineering](https://www.springer.com/journal/10664/), Volume 27, 25, 2022.<br/>
Download:[[PDF](https://link.springer.com/content/pdf/10.1007/s10664-021-10063-9.pdf)]

<br/>

Chenxi Zhang, Xin Peng, Chaofeng Sha, Ke Zhang, Zhenqing Fu, Xiya Wu, Qingwei Lin, Dongmei Zhang<br/>
**DeepTraLog: Trace-Log Combined Microservice Anomaly Detection through Graph-based Deep Learning**<br/>
In Proceedings of the 44th International Conference on Software Engineering ([ICSE 2022](https://dblp.uni-trier.de/db/conf/icse/icse2022.html)) , Pittsburgh, USA, May, 2022.<br/>
Download:[[PDF](https://dl.acm.org/doi/pdf/10.1145/3510003.3510180)]

<br/>
	
Dewei Liu, Chuan He, Xin Peng, Fan Lin, Chenxi Zhang, Shengfang Gong, Ziang Li, Jiayu Ou, Zheshun Wu<br/>
**MicroHECL: High-Efficient Root Cause Localization in Large-Scale Microservice Systems**<br/>
In Proceedings of the 43rd IEEE/ACM International Conference on Software Engineering: Software Engineering in Practice ([ICSE-SEIP 2021](https://dblp.uni-trier.de/db/conf/icse/seip2021.html#LiuH0LZGLOW21)) , Madrid, Spain, May, 2021.<br/>
Download:[[PDF](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9402058)]

<br/>

Qilin Xiang, Xin Peng, Chuan He, Hanzhang Wang, Tao Xie, Dewei Liu, Gang Zhang, Yuanfang Cai<br/>
**No Free Lunch: Microservice Practices Reconsidered in Industry**<br/>
arXiv preprint arXiv:2106.07321, 2021.<br/>
Download:[[PDF](https://arxiv.org/pdf/2106.07321.pdf)]

<br/>

Xiaofeng Guo, Xin Peng, Hanzhang Wang, Wanxue Li, Huai Jiang, Dan Ding, Tao Xie, Liangfei Su<br/>
**Graph-based trace analysis for microservice architecture understanding and problem diagnosis**<br/>
In Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering ([ESEC/FSE 2020](https://dblp.uni-trier.de/db/conf/sigsoft/fse2020.html)) , Virtual Event, USA, November, 2020.<br/>
Download:[[PDF](https://dl.acm.org/doi/pdf/10.1145/3368089.3417066)]

<br/>


Xiang Zhou, Xin Peng, Tao Xie, Jun Sun, Chao Ji, Dewei Liu, Qilin Xiang, and Chuan He. <br/>
**Latent Error Prediction and Fault Localization for Microservice Applications by Learning from System Trace Logs.**<br/>
In Proceedings of the 27th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering ([ESEC/FSE 2019](https://dblp.uni-trier.de/db/conf/sigsoft/fse2019.html)) , Tallinn, Estonia, August 2019. <br/>
Download: [[PDF](https://cspengxin.github.io/publications/fse19-zhou-microservice.pdf)] [[BibTeX](https://dblp.uni-trier.de/rec/bibtex/conf/sigsoft/Zhou0X0JLXH19)] 

<br/>

Xiang Zhou, Xin Peng, Tao Xie, Jun Sun, Chao Ji, Wenhai Li, and Dan Ding. <br/>
**Fault Analysis and Debugging of Microservice Systems: Industrial Survey, Benchmark System, and Empirical Study.** <br/>
[IEEE Transactions on Software Engineering](https://www.computer.org/web/tse) , To appear. <img src="image/cup.png" height="20px"/> <img src="image/tse-best-paper-award.png" height="28px"> <br/> 
Download: [[PDF](https://cspengxin.github.io/publications/tse19-msdebugging.pdf)] 

<br/>

Xiang Zhou, Xin Peng, Tao Xie, Jun Sun, Wenhai Li, Chao Ji, and Dan Ding. <br/>
**Delta Debugging Microservice Systems.** <br/>
In Proceedings of 33rd IEEE/ACM International Conference on Automated Software Engineering ([ASE 2018](http://ase2018.com/)) , Short Paper, Montpellier, France, September 2018. <br/>
Download: [[PDF](https://cspengxin.github.io/publications/ase18-debugmicroservice.pdf)] [[BibTeX](https://dblp.uni-trier.de/rec/bibtex/conf/kbse/ZhouPX0LJD18)] <br/>
An extended version to appear in IEEE Transactions on Services Computing. 

<br/>

Xiang Zhou, Xin Peng, Tao Xie, Jun Sun, Chenjie Xu, Chao Ji, and Wenyun Zhao. <br/>
**Poster: Benchmarking Microservice Systems for Software Engineering Research.** <br/>
In Proceedings of the 40th International Conference on Software Engineering ([ICSE 2018](https://www.icse2018.org/)) , Posters, Gothenburg, Sweden, May 2018. <br/>
Download: [[PDF](https://cspengxin.github.io/publications/icse18poster-microservices.pdf)] [[BibTeX](https://dblp.uni-trier.de/rec/bibtex/conf/icse/ZhouPX0XJZ18)] 



