# Local Chatbot

## Chatbot Pipeline

![Chatbot Pipeline](../Images/Pipeline.png)

## Installing Local Embedding Models

- Navigate to the notebook directory and open it:

  ```bash
  cd ..\CSE299\chatbot\rag_tests
  jupyter notebook Install_Local_HuggingFace_EmbeddingModels.ipynb
  ```

- Follow the instructions in the notebook to install embedding models.
- Create the embedded vector database using chunking methods (character/recursive/semantic).
- Embedded vector database can be created in any cloud service and downloaded for use, but the embedding models must be installed locally.

## MongoDB Setup

- **Start MongoDB**:  

  ```bash
  mongod --dbpath /path/to/your/db --port 27017
  ```

- **Initialize the Database**:

  ```bash
  cd ..\CSE299\chatbot\Backend\MongoDB
  python dummy_2.py
  ```

## Running the Chatbot

- **Frontend**:

  ```bash
  cd ..\CSE299\chatbot\Frontend
  streamlit run stream_app.py
  ```

- **Backend**:

  ```bash
  cd ..\CSE299\chatbot\Backend
  python stream_app.py
  ```
