from fastapi import FastAPI,Query

app=FastAPI(title="First API") 

BLOG_APP=[
    {"id":1,"title":"mi primer post","content":"este es mi primer post"},
    {"id":2,"title":"mi segundo post","content":"este es mi segundo post"},
    {"id":3,"title":"mi tercer post","content":"este es mi tercer post"},
]


@app.get("/")
def home():
    return {'message':'Hello World from FastAPI'} 

@app.get("/posts")
def list_posts(query:str|None=Query(default=None,description="Parametro para buscar blogs")):  
    if query:  
        results=[post for post in BLOG_APP if query.lower() in post['title'].lower()]
        return {"data":results}
    else:
        return {"data":BLOG_APP}