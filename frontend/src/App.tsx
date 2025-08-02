// top section: search bar, logo, and navigation options + settings
// left section: gemma 3 4b results on top, search results below
// right section: universal results on top, image search results below (two images per row, about 14 images); no more internal tabs. list all possible universal results stacked on the right section. combined with the image results, the right section is longer than the left section. the left section will be blank space if this is the case; for example, if two wiki results and one spotify result is called, list all wiki results with the spotify result below the two wiki results. below the spotify result is the images. news results from brave

// for home page: links to directly search for the web, images, videos, or news; news stories below (takes up left section, 2/3 of the width); 1/3 of the rest of the the width, on the right side are example queries to try out. example queries box does not scroll and it stays fixed in place

// constanly check if the cookie is empty. if there is a session id in the cookie, take the id and call redis endpoint. if not, call the route to create a new session id

// if any errors arise (if the response is success: false), make a pop-up that can be closed by clicking on the OK button; make sure the pop-up is on the center top of the page, small in size. do not take up too much of the screen