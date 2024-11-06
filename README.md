# README #
Setup
Copy `.env.tmp` to `.env`, then edit with your API keys and credentials

Run the application
```
python ./src/app.py
```
## Testing

### Embedding
Embedding models are evaluated on: 
- cost
- accuracy
#### Cost
Evaluating embedding cost is simple: what is the per-token quoted cost?
The table below outlines the field:

| Model                | Cost/1k tokens |
|----------------------|----------------|
| OpenAI Ada 2         | $0.0001        |
| AWS Titan            | $0.0001        |
| AWS Titan Multimodal | $0.0008        |
| Cohere Embed         | $0.0001        |


#### Retrieval Accuracy

A testing benchmark has been prepared to test fragment retrieval accurracy.
The benchmark application can be run as follows:
```
python ./src/embeddings_tester.py
```
The application is used through a browser.
Scores are shown below.
| Model                | % Score |
|----------------------|---------|
| OpenAI Ada 2         |         |
| AWS Titan            |         |
| AWS Titan Multimodal |         |
| Cohere Embed         |         |