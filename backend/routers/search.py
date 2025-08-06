# also include brave suggest for predictive search; call useEffect each time the user types in a new word
# use gemma 3 12b-it
# use from fastapi.responses import StreamingResponse to stream the llm response
# search on google for reference: openrouter api streaming python fastapi to frontend exxmaple
# post endpoint will be sent back as a package, with brave search results and brave image results (images displayed on right side)
# in the same route that calls the brave api, in the end of the route, if the user isn't logged in, update the redis session and store the user query to the logged out search history; if they are logged in, call the rds method for entering the user query to the user_search_history. do this by asking for a query parameter of the session id
# if the function returns falsy, send a notice to the user; make sure it tells all possible scenarios ex: make sure to use a compatible file type (.jpeg, .pdf, .png, .jpg) and/or check your connection, something went wrong with our system, etc.