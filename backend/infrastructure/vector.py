from pinecone import Pinecone
# later, create helper functions that allow for entering vector emebdded text into the vector db and retrieving similar nearest neighbor vector embedded text from pinecone based on a vector embedded query
# import openai vector embedding api. functions will take in regular text and in the function the text will use openai api to convert it to vector embeddings
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX_NAME")

if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region=os.getenv("PINECONE_INDEX_REGION"),
        embed={
            "model": "llama-text-embed-v2",
            "field_map": {"text": "chunk_text"}
        }
    )
    
index = pc.Index(index_name)
