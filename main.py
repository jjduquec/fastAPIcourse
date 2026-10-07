from fastapi import FastAPI,Query,Body

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

@app.get("/post/{id}")
def get_post(id:int,get_content:bool=Query(default=True,description="Parametro para recuperar o no el contenido de un post")):
    for post in BLOG_APP:  
        if post["id"]==id:  
            if not get_content: 
                data={"id":post["id"],"title":post["title"]} 
            else: 
                data=post  
            return {"data":data} 
    return {"data":"Post no encontrado"}

@app.post("/post")
def create_post(post:dict=Body(...)):
    if "title" not in post or "content" not in post: 
        respuesta={"error":"el post debe contener titulo y contenido"} 
    elif not str(post["title"]).strip():  
        respuesta={"error":"el titulo no puede estar vacio"}

    else:  
        new_id=len(BLOG_APP)+1 
        post["id"]=new_id 
        BLOG_APP.append(post) 
        respuesta={"message":"el post se ha creado exitosamente"}