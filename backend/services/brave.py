# helper functions for all brave apis (brave web search, brave news, brave images, brave videos, suggest); take extra snippets from search results, call pinecone helper function to add to vector db

# use confluent kafka to avoid RPS constraints
# use rate limiter for all services