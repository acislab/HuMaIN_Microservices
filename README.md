# HuMaIN_Microservices
Reusable information extraction and image processing microservices. Based on [OCRopy](https://github.com/tmbdev/ocropy) and its library [ocrolib](https://github.com/tmbdev/ocropy/tree/master/ocrolib) and [Tesseract](https://github.com/tesseract-ocr/tesseract)

Containing:<br/>
1) Four microservices: Binarization, Segemntation, Recognition and Tesseract services.<br/>
2) One OCRopy application, which implemented by invoking Binarization, Segmentation and Recognition services. Useful for users who want to use OCRopy to extract the image information directly.<br/>

All microservices **handle images in memory** directly.<br/>

## Setup of Microservices
Four ways (details are introduced in README.md of each microservice project):<br/>

* Way-1: Deploy each microservice on the Django built-in server.<br/>
Pros: quick to work.<br/>
Cons: can only handle one request each time.<br/>

* Way-2: Deploy each microservice on Apache server.<br/>
Pros: can handle multiple requests concurrently.<br/>

* Way-3: Deploy from Docker image.<br/>
Pros: needn’t to download and deploy the microservice.<br/>

* Way-4: Deploy with Kubernetes (K8s).<br/>
Pros: can handle multiple requests concurrently, and auto-scale the number of instances of microservice to improve its performance remarkably.

## Test Scripts
For each microservice/application we created a script used to simulate to invoke the microservice. Besides, the scripts support to send multiple requests concurrently.<br/>
Take the Binarization service script as example, we can use the following command to check how to use it:<br/>
```
$ python call_bin_multiP.py --help
```

## Management of Microserivices Using K8s and Istio
In the devolopment environment, we deployed these microservices on Kubernetes and manage them with Istio. We provided three sample configuration files *'ocr-gateway.yaml'*, *'route-rule-ocr.yaml'* and *'virtual-service-ocr.yaml'* under directory 'Istio-manifests/' to show how we configure the gateway and route rules in Istio.
