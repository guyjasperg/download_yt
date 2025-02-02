Problems encountered

1. pytubefix requiring poToken in order to download from youtube.

Fix:

Need to add poToken (and visitorData?). use youtube-po-token-generator (https://github.com/YunzheZJU/youtube-po-token-generator) to get the 
poToken. just run "node /examples/one-shot.js" to generate.

pytubefix's YouTube class may need to be modified if support for poToken is not yet added.
go to 
"/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/pytubefix/__main__.py"

update Youtube class.

class YouTube:
    """Core developer interface for pytubefix."""

    def __init__(
            self,
            url: str,
            .
            .

           use_po_token: Optional[bool] = False,
            po_token: Optional[str] = None,     <-- add this

.
.
.
        self.use_oauth = use_oauth
        self.allow_oauth_cache = allow_oauth_cache
        self.token_file = token_file
        self.oauth_verifier = oauth_verifier

        self.use_po_token = use_po_token
        self.po_token_verifier = po_token_verifier

        self.po_token = po_token    <-- add this

    def __repr__(self):


And then in your app, after you have generated the poToken, use it.:

    try:
        try:
            message_queue.put("\ncontacting server...")
            
            # modified YouTube class to use po_token paramater            
            yt = YouTube(url,use_po_token=True, po_token=PO_TOKEN, on_progress_callback=on_progress )
