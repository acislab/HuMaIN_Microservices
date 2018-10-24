# HuMaIN_Microservices
Reusable information extraction and image processing microservices. Based on [OCRopus](https://github.com/tmbdev/ocropy) and its library [ocrolib](https://github.com/tmbdev/ocropy/tree/master/ocrolib) and [Tesseract](https://github.com/tesseract-ocr/tesseract)

Containing:<br/>
1) Four microservices: Binarization, Segemntation and Recognition under directory ‘OCR/OCRopus/ and Tesseract under directory ‘OCR/’.<br/>
2) One OCRopy (OCRopus) application under directory ‘OCR/’, which implemented by invoking Binarization, Segmentation and Recognition services. Useful for users who want extract the image information directly.<br/>

All microservices **processing images in memory**, different with [OCRopus](https://github.com/tmbdev/ocropy) which need to store the intermediate data locally.<br/>

## Deployment of Microservices
Four ways (details are introduced in README.md of each microservice project):<br/>

* Way-1: Deploy each microservice on the Django built-in server.<br/>
Pros: quick to work.<br/>
Cons: can only handle one request each time.<br/>

* Way-2: Deploy each microservice on Apache server.<br/>
Pros: can handle multiple requests concurrently.<br/>

* Way-3: Deploy from Docker image.<br/>
Pros: needn’t to download and deploy the microservice.<br/>

* Way-4: Deploy with Kubernetes.<br/>
Pros: can handle multiple requests concurrently, and auto-scale the number of instances of microservice to improve its performance remarkably.
