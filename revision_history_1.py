from mw import api
from mw.lib import persistence

# Initialize api session and page state
session = api.Session("https://en.wikipedia.org/w/api.php")
page_state = persistence.State()

# Query for the page's revisions
# returns an iterator of rev dicts from the API.
# http://pythonhosted.org/mediawiki-utilities/core/api.html#mw.api.Revisions.query
rev_docs = session.revisions.query(titles={"City of San Marino"},
                                   properties={"content", "user", "timestamp", "sha1"},
                                   direction="newer")

# Use the page_state to process the revisions (and store the revision's timestamps)
# page_state.process returns three tokens: current_token, tokens_added, tokens_removed
# http://pythonhosted.org/mediawiki-utilities/lib/persistence.html#mw.lib.persistence.State.process
last_tokens = None
for rev_doc in rev_docs:
    tokens, _, _ = page_state.process(rev_doc.get("*", ""),
                                      rev_doc['timestamp'],
                                      checksum=rev_doc['sha1'])
    #tokens has a list of tokens and their revison histories
    last_tokens = tokens
print("Length of extracted tokens:",len(last_tokens))

#for t in last_tokens:
#    print(t.text)
# This gnarely bit of code is just used to find the specific tokens we are looking for
# http://pythonhosted.org/mediawiki-utilities/lib/persistence.html#tokenization
expected = "The city has a population of 4,128"
len_expected = len(persistence.tokenization.wikitext_split(expected))
print("Length of expected tokens:",len_expected, "\nExpected tokens: ", persistence.tokenization.wikitext_split(expected))
match_ranges = [(i, i+len_expected) for i in range(len(last_tokens))
                                    if "".join(t.text for t in last_tokens[i:i+len_expected]) == expected]
#match_ranges finds out where the 'expected' text appears in the wiki and returns index ranges for the same.

# Print out the tokens and the first revision they appeared in
print("\nRevision history of all matching tokens:")
for start, end in match_ranges:
    for token in last_tokens[start:end]:
        if len(token.text.strip()) == 0: continue #ignoring spaces
        print("'{0}' was added {1}".format(token.text, token.revisions[0]))

'''for token in last_tokens:
        if len(token.text.strip()) == 0: continue #ignoring spaces
        print("'{0}' was added {1}".format(token.text, token.revisions[0]))'''

# Since we are checking the accuracy of the article's statistics (generally numeric, in this example, the population 4,123),
# I am going to pull up only those tokens for analysis
print("\nPulling up only numeric tokens:")
for start, end in match_ranges:
    for token in last_tokens[start:end]:
        if len(token.text.strip()) == 0: continue #ignoring spaces
        if token.text.isnumeric() == False: continue
        print("'{0}' was added {1}".format(token.text, token.revisions[0]))
